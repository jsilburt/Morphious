import pandas as pd
import os
import numpy as np
import pdb
from datetime import datetime, date


### post-analysis functions ###

def regroup_data(df, groups):
    """assigns an analysis group to each file in the dataframe

    Args:
        df (pandas dataframe): dataframe of analysis data
        groups (dictionary): filename : group dictionary

    Returns:
        pandas dataframe: dataframe of re-assigned data
    """
    df = df.set_index('file')
    for k,v in groups.items():
        df.loc[k, 'analysis_group'] = v
    df.loc[:, 'analysis_group'] = df['analysis_group'].replace('', np.nan)
    df = df.dropna(subset=['analysis_group'])
    return df.reset_index()

def is_cluster_area(series):
    """determines whether a dataseries was taken from a cluster, or whole image

    Args:
        series (pandas dataseries): data from one file

    Returns:
        boolean: whether the file was taken from a cluster area
    """
    is_cluster=False

    bg_cols = np.array(['ImageBackgroundArea', 'ClusterBackgroundArea'])
    if (np.intersect1d(series.index.values, bg_cols).shape[0] == 0):
        print("ERROR, files do not contain either of the columns, 'ImageBackgroundArea', 'ClusterBackgroundArea' \n did you use the wrong script?")

    if (series['ClusterBackgroundArea'].astype(float) > 0):
        is_cluster=True
    return is_cluster

def IF_and_cluster_analysis(df):
    """
    groups dataframe if necessary and calculates mean intensity and perc area, data is normalized to a background area.
    if the dataframe is a cluster area, the cluster size is determined

    Parameters
    ----------
    df : pandas dataframe
        dataframe containing the immunofluorescence features, must contain the columns ['file', 'IntDen', 'Area', 'BackgroundArea']

    Returns
    -------
    df : pandas dataframe
        dataframe of evaluated IF metrics
    """
    grp_str, has_clusters, bg_area = config_regrouping(df)
    dat = IF_analysis(df, bg_area=bg_area)

    if has_clusters:
        cl = cluster_analysis(df)
        cl_cols = np.setdiff1d(cl.columns.values, dat.columns.values).tolist()
        cl = cl[cl_cols + ['analysis_group']]
        dat = pd.merge(dat, cl, on='analysis_group')
    df = pd.merge(dat, grp_str, on='analysis_group', how='left')
    return df

def skeleton_and_cell_analysis(skel_df, cell_df):
    """performs skeleton and cell analysis

    Args:
        skel_df (pandas dataframe): dataframe with skeleton data
        cell_df (pandas dataframe): dataframe with cell data

    Returns:
        pandas dataframe: dataframe with completed analysis
    """
    if cell_df is not None:
        cell_df = cell_analysis(cell_df)
        df = cell_df
    if skel_df is not None:
        skel_df = skeleton_analysis(skel_df, cell_df=cell_df)
        df = skel_df
    return df

def cell_analysis(df, features=['Area', 'Perim.', 'cell_counts', 'nnd']):
    """analyzes cell data, data is normalized to a background area

    Args:
        df (pandas dataframe): dataframe with cell data
        features (list, optional): features to include to be summed for analysis. Defaults to ['Area', 'Perim.', 'cell_counts', 'nnd'].

    Returns:
        pandas dataframe: dataframe with analyzed data
    """
    grp_str, _, bg_area = config_regrouping(df)
    df = df.groupby('analysis_group')[features + [bg_area]].sum().reset_index()
    df.loc[:, 'cell_density_per_100um2'] = (df['cell_counts'] / df[bg_area]) * 100**2
    df.loc[:, 'mean_nnd_per_cell'] = df['nnd'] / df['cell_counts']
    df.loc[:, 'mean_soma_size_per_cell'] = df['Area'] / df['cell_counts']
    df = pd.merge(df, grp_str, on='analysis_group', how='left')
    return df

def skeleton_analysis(df, cell_df=None, skel_features=['# Branches', '# Junctions', '# End-point voxels', '# Triple points', '# Quadruple points', 'TotalBranchLength']):
    """analyzes skeleton data, data is normalized to a background area, and cell counts if applicable

    Args:
        df (pandas dataframe): dataframe with skeleton data
        cell_df (pandas dataframe, optional): dataframe with processes cell analysis, if included skeleton data will be normalized to cell counts. Defaults to None.
        skel_features (list, optional): skeleton features to be summed for analysis. Defaults to ['# Branches', '# Junctions', '# End-point voxels', '# Triple points', '# Quadruple points', 'TotalBranchLength'].

    Returns:
        pandas dataframe: dataframe with analyzed data
    """
    grp_str, _, bg_area = config_regrouping(df)
    df = df.groupby('analysis_group').sum().reset_index()
    df = pd.merge(df, grp_str, on='analysis_group', how='left')
    for f in skel_features:
        df.loc[:, f"{f}_per_100um2"] = (df[f] / df[bg_area]) * 100**2
    df.loc[:, ' ']
    if cell_df is not None:
        cell_cols = np.setdiff1d(cell_df.columns.values, df.columns.values).tolist() + ['analysis_group']
        df = pd.merge(df, cell_df[cell_cols], on='analysis_group', how='inner')
        for f in skel_features:
            df.loc[:, f"{f}_per_cell"] = (df[f] / df['cell_counts'])
    return df

def config_regrouping(df):
    """configuration information for the analysis, including the regrouped groupings, whether to perform cluster analysis, the background area choice

    Args:
        df (pandas dataframe): dataframe to configure

    Returns:
        list: dataframe of regrouping labels, is a cluster area, background area choice
    """
    grp_files = df.groupby('analysis_group')['file'].apply(list)
    grp_str = grp_files.apply(lambda x: "_".join(x)).reset_index()
    has_clusters = is_cluster_area(df.iloc[0])
    bg_area = 'ImageBackgroundArea'
    if(has_clusters):
        bg_area = "ClusterBackgroundArea"
    return grp_str, has_clusters, bg_area
    
def save_file(df, path, fname):
    """save dataframe to a file, adds a timestamp

    Args:
        df (pandas dataframe): dataframe to save
        path (str): output path
        fname (str): file name
    """
    ts = datetime.today().strftime('%Y-%m-%d-%Hh-%Mm-%Ss')
    out_path = os.path.join(path, f"{ts}_{fname}.csv")
    df.to_csv(out_path)

def IF_analysis(df, bg_area='ImageBackgroundArea'):
    """performs immunoflourescence analysis, normalizes data to a background area

    Args:
        df (pandas dataframe): dataframe of immunofluorescence data
        bg_area (str, optional): background area to normalize data to. Defaults to 'ImageBackgroundArea'.

    Returns:
        pandas dataframe: dataframe of analyzed immunofluorescense data
    """
    df = df.groupby('analysis_group')[['IntDen', 'Area', bg_area]].sum().reset_index()
    df.loc[:, 'MeanIntensity'] = df.loc[:, 'IntDen'] / df['Area']
    df.loc[:, 'PercArea'] = df.loc[:, 'Area'] / df.loc[:, bg_area]
    return df

def cluster_analysis(df):
    """calculates cluster size

    Args:
        df (pandas dataframe): dataframe that contains the columns, 'ClusterBackgroundArea' and 'ImageBackgroundArea'

    Returns:
        pandas dataframe: dataframe with cluster area
    """
    df = df.groupby('analysis_group')[['ClusterBackgroundArea', 'ImageBackgroundArea']].sum().reset_index()
    df.loc[:, 'PercentClusterArea'] = df['ClusterBackgroundArea'] / df['ImageBackgroundArea']
    return df





