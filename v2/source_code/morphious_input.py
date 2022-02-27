# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 22:13:35 2020

@author: joey_
"""
import pandas as pd
import numpy as np
import os
import time

from scipy import spatial
import numpy.matlib
import gc
import copy
#import decimal

import pdb


      
'''
def set_box_id(mice):
    mice.loc[:,"boxID"] = np.arange(0,len(mice))
    return mice
'''

def round_digits(df,features=['BX','BY']):
    '''
    rounds selected features to 1 decimal point

    Parameters
    ----------
    df : pandas dataframe
        dataframe containing the features to round.
    features : list-like, optional
        features to be rounded. The default is ['BX','BY'].

    Returns
    -------
    df : pandas dataframe
        dataframe with rounded digits.
    '''
    df.loc[:,features] = df[features].astype('float').round(1)
    return df

def add_all_cell_data2(mice,boxsize=150,
                       path="",
                      nnd=True, coords = ['BX', 'BY'], centers=['X','Y'], keys=['file'], fill_nan=True, slide=2, scale=1.5
                      ):
    '''
    integrates cell soma data into a feature map grid.

    Parameters
    ----------
    mice : pandas dataframe
        feature map data for which the cell data is to be integrated into.
    boxsize : int, optional
        size of the boxsize in the feature map grid. The default is 150.
    path : string, optional
        location of the cell data. The default is "".
    nnd : boolean, optional
        calculate the nearest neighbour distance between cell soma. The default is True.
    coords : list-like, optional
        xy coordinate denoting the spatial coordinates of features in the 'mice' dataframe. The default is ['BX', 'BY'].
    centers : list-like, optional
        xy coordinate features to refer to cordinates of the cell somas. The default is ['X','Y'].
    keys : list-like, optional
        unique identifier to refer to individual images/samples. The default is ['file'].
    fill_nan : boolean, optional
        replaces missing feature data with 0. The default is True.
    slide : int, optional
        corresponds to the offset determined at feature generation, 
        inversely proportional to the degree of overlap between neighbouring boxes in the feature map. The default is 2.
    scale : float, optional
        the svale of the initial images in um/pixel. The default is 1.5.

    Returns
    -------
    mice : pandas dataframe
        features with cell data integrated.

    '''
    begin=time.time()
    files = os.listdir(path)

    to_add = []
    for f in files:
        print(f)
        st = time.time()
        #ms, day, cond, cell, sect = f.split("_")
        sec = pd.read_csv(path+f,sep="\t")
        sec = sec.rename(columns={" " : "cellID"})
        sec.loc[:, 'file'] = f.replace(".txt", "")
        if nnd:
            nnd_df = construct_nnd_df(sec, xy=centers)
            sec = pd.merge(sec, nnd_df, on=centers)
            
            to_add.append(sec)
         
    to_add = pd.concat(to_add,ignore_index=True)
    mice = add_cell_data3(mice,to_add, indeces = keys, xy = coords, cell_centers = centers,
                          boxsize=boxsize, scale=scale, slide=slide)
    
    #calculate soma features
    mice.loc[:,'ave_nnd'] = mice.loc[:,'sum_cell_nnd'] / mice.loc[:,'cell_counts']
    mice.loc[:,'ave_soma_size'] = mice.loc[:,'sum_cell_area'] / mice.loc[:,'cell_counts']
    mice.loc[:,'ave_soma_circularity'] = (4* np.pi * mice.loc[:,'sum_cell_area']) / (mice.loc[:,'sum_cell_perim_squared']) #4Ï€â€…Ã—â€…[Area] / [Perimeter]**2
    
    if fill_nan:
        mice.fillna(value=0, inplace=True)
    
    #print('total_time: ', time.time()-begin)
    return mice

'''
def align_cellfeats_index(cells,index_names,index,xy=['BX','BY'],decimals=3):
    for k, v in zip(index_names,index):
        cells.loc[:,k] = v
    return cells.set_index(index_names+xy)

def get_ranges2(rangeinindex,xy,slide=2,slide_size=100):
    range_ = np.unique(rangeinindex.index.get_level_values(xy))
    ranges = []
    for i in range(0,slide):
        _ = np.arange(i,len(range_),slide)
        #for cut need to add one more upper boundary so the previous upper boundary is considered
        last = range_[_[-1]]
        grid = range_[_]
        
        grid = np.append(grid,[last+slide_size])
        ranges.append(grid)
    return ranges
'''

def add_cell_data3(main, cells, indeces=['file'],
                   xy=['BX','BY'],
                   cell_centers=['X','Y'],
                   boxsize=150,scale=1.5,slide=2,decimals=1):
    '''
    

    Parameters
    ----------
    main : pandas dataframe
        base feature map for which cell soma data is to be added into.
    cells : pandas dataframe
        cell soma data.
    indeces : list-like, optional
        unique identifier to refer to individual images/samples. The default is ['file'].
    xy : list-like, optional
        features refering to the spatial coordinates of the feature map grid present in 'main'. The default is ['BX','BY'].
    cell_centers : list-like, optional
        features refering to the xy coordinates of the cell somas. The default is ['X','Y'].
    boxsize : int, optional
        size of the boxes in the feature grid. The default is 150.
    scale : int, optional
        scale of the original iamges in um/pixel. The default is 1.5.
    slide : int, optional
        corresponds to the offset determined at feature generation, 
        inversely proportional to the degree of overlap between neighbouring boxes in the feature map. The default is 2.
    decimals : int, optional
        number of decimal places to round the coordinates to. The default is 1.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    counting_frames = []
    cells.loc[:,'perim_squared']=cells['Perim.']**2
    to_add = cells.loc[:, indeces+cell_centers+['Area','Perim.','perim_squared','cellID','nnd']]
    square_length = boxsize / scale 
    skew = boxsize / scale / slide #the magnitude of the translation between boxes
    #print(square_length)
    
    all_frameshifts = []
    #shift across all possible boxes, and add cells whose center fit within the upper and lower bounds of each box
    for x in range(0, slide):
        for y in range(0, slide):
            x_range = ((to_add[cell_centers[0]] - (skew * x)) / square_length) #subtract 50
            y_range = ((to_add[cell_centers[1]] - (skew * y)) / square_length)
            to_add.loc[:,'grid_x'] = x_range
            to_add.loc[:,'grid_y'] = y_range
            x_range = x_range.loc[x_range>=0].apply(int) #int(-0.###) == 0 which is incorrect assignment
            y_range = y_range.loc[y_range>=0].apply(int)
            
            to_add.loc[:,xy[0]] = round(x_range * square_length + (skew * x)) #round bx and by coordinates so it matches with feature grid coordinates
            to_add.loc[:,xy[1]] = round(y_range * square_length + (skew * y))
            
            #print(to_add)
            all_frameshifts.append(copy.copy(to_add))
    
    to_add = pd.concat(all_frameshifts)
    to_add = to_add.dropna(subset=['BX','BY'])

    main = main.set_index(indeces+xy).sort_index()
    to_add = to_add.groupby(indeces+xy)[['cellID','Area','perim_squared','nnd']].agg({'cellID':'count',
                                                                             'Area': 'sum',
                                                                             'perim_squared': 'sum',
                                                                             'nnd': 'sum'})
    to_add = to_add.rename(columns = {'cellID' : 'cell_counts',
                                      'Area':'sum_cell_area', 
                                      'perim_squared' : 'sum_cell_perim_squared',
                                      'nnd': 'sum_cell_nnd'})
    
    main = pd.merge(main, to_add, on=indeces+xy, how='outer')
    
    return main.reset_index()

def do_kdtree(xy,points):
    '''
    generates tree diagram to find the pair-wise nearest neighbours between the points in two arrays

    Parameters
    ----------
    xy : list-like
        first set of coordinates.
    points : list-like
        second set of coordinates.

    Returns
    -------
    TYPE
        distance between point.
    index : TYPE
        index of nearest neighbours.

    '''
    mytree = spatial.cKDTree(xy)
    return mytree.query(points,k=2) # dist, index
    
def get_nnd(xy):
    '''
    computes the nearest neighbour distance for each point in a list

    Parameters
    ----------
    xy : list-like
        a list of points.

    Returns
    -------
    point1 : list-like
        first set of points.
    point2 : list-like
        nearest neighbouring points.
    distances : list-like
        distances of nearest neighbour points.

    '''
    dist, ind = do_kdtree(xy,xy)
    point1=xy
    point2=xy[ind[:,1]]
    distances=dist[:,1]
    return point1, point2, distances

def construct_nnd_df(df,xy=['X','Y']):
    '''
    constructs a dataframe of nearest neighbours.

    Parameters
    ----------
    df : pandas dataframe
        contains the xy coordinates of points for which the NND is to be computed.
    xy : list-like, optional
        coordinates columns. The default is ['X','Y'].

    Returns
    -------
    pandas dataframe
        dataframe with the NND computed.

    '''
    p1, p2, d = get_nnd(df[xy].values)
    comb = np.column_stack((p1,d))
    return pd.DataFrame(comb,columns=xy+['nnd'])


#read the brain section features file which is identified by mouseID, day, treatment, celltype, sectionID
#return a pd.dataframe containing a section's main features
def read_mouse_features_file(file, path="",delim="\t", split_by = None):
    '''
    read feature data into a pandas data frame.

    Parameters
    ----------
    file : string
        file name to be read into a pandas data frame.
    path : string, optional
        path to file. The default is "".
    delim : string, optional
        delimiter to read file data with. The default is "\t".
    split_by : string, optional
        split the file name by a value, retrieve the first part of the file. The default is None.

    Returns
    -------
    d : pandas dataframe
        dataframe containing feature data for the file.

    '''
    f = f"{path}/{file}"
    d = pd.read_csv(f,delimiter=delim)
    if split_by is not None:
        file = file.split(split_by)[:-1] #remove _boxsize-boxsize in skeleton path
        file = f"{split_by}".join(file)
    d.loc[:, 'file'] = file.replace(".txt","") #remove .txt
        
    return d
    
def read_mouse_features(path="",delim="\t",split_by = None):
    '''
    read all feature files in a directory into a dataframe 

    Parameters
    ----------
    path : list-like, optional
        path to files to be loaded. The default is "".
    delim : string, optional
        delimiter to split feature file data with. The default is "\t".
    split_by : string, optional
        split the file name by a value, retrieve the first part of the file. The default is None.
     

    Returns
    -------
    allMice : pandas dataframe
        feature data.

    '''
    mice = []
    files = os.listdir(path)
    
    print("--- reading features files ---")
    for f in files:
        print(f)
        mice.append(read_mouse_features_file(f,path=path,delim=delim, split_by=split_by))
    allMice = pd.concat(mice,ignore_index=True)
    return allMice

def compile_feature_df(
        feature_path = None,
        fractal_path = None,
        skeleton_path = None,
        cell_count_path = None,
        _slide=2,
        boxsize=150,
        scale=1.5,
        coords = ['BX','BY'],
        groupby = ['file']):
    '''
    all in one convenience function to load all data into a single data frame

    Parameters
    ----------
    feature_path : string, optional
        path to intensity features data. The default is None.
    fractal_path : string, optional
        path to fractal dimensional data. The default is None.
    skeleton_path : string, optional
        path to skeleton data. The default is None.
    cell_count_path : string, optional
        path to cell feature data. The default is None.
    _slide : Int, optional
        corresponds to the offset determined at feature generation, 
        inversely proportional to the degree of overlap between neighbouring boxes in the feature map. The default is 2.
    boxsize : int, optional
        size of the boxsize in the feature map grid. The default is 150.
    scale : int, optional
        scale of the original iamges in um/pixel. The default is 1.5.
    coords : list-like, optional
        xy coordinate denoting the spatial coordinates of features in the 'mice' dataframe. The default is ['BX', 'BY'].
    groupby : list-like, optional
        Indexes to uniquely identify samples/images. The default is ['file'].

    Returns
    -------
    df : pandas dataframe
        dataframe with all feature data.

    '''
    
    feature_dfs = []
    branch_feature_dfs = []
    fractal_dfs = []
    
    all_dfs = []
    
    if feature_path:
        feature_dfs.append(read_mouse_features(path=feature_path))
        feat_df = round_digits(pd.concat(feature_dfs))
        all_dfs.append(feat_df)
    if skeleton_path:
        branch_feature_dfs.append(read_mouse_features(path=skeleton_path,split_by="_"))
        branch_df = round_digits(pd.concat(branch_feature_dfs))
        all_dfs.append(branch_df)
    if fractal_path:
        fractal_dfs.append(read_mouse_features(path=fractal_path))
        fract_df = round_digits(pd.concat(fractal_dfs))
        all_dfs.append(fract_df)
    
    df = all_dfs[0]
    if len(all_dfs) > 1:
        #print('accessed')
        for df2 in all_dfs[1:]:
            df = pd.merge(df, df2, on=coords+groupby, how="outer")
            #print(df.shape)
            
    if cell_count_path:
        df = add_all_cell_data2(df,boxsize=boxsize,nnd=True,slide=_slide,
                                scale = scale,
                                path=cell_count_path+"/")
        gc.collect()
        
    df.loc[:,'boxID'] = df.reset_index().index.values

    return df


    ### read post-analysis files ###
def read_IF_anal_data(path, sep="\t"):
    """read immunoflourescence data files

    Args:
        path (str): path to immunofluorescence files
        sep (str, optional): delimiter of files. Defaults to "\t".

    Returns:
        pandas dataframe: dataframe of immunofluorescence data
    """
    df = pd.concat([read_and_file_stamp(path, f, (i*-1)-1) for i, f in enumerate(os.listdir(path))]).reset_index(drop=True) #open and read files
    return df

def read_skel_anal_data(path, sep="\t"):
    """read skeleton data files

    Args:
        path (str): path to skeleton files
        sep (str, optional): delimiter of files. Defaults to "\t".

    Returns:
        pandas dataframe: dataframe of skeleton data
    """
    df = pd.concat([read_and_file_stamp(path, f, (i*-1)-1, skel_file=True) 
        for i, f in enumerate(os.listdir(path))
        if is_skel_file(f)]
        ).reset_index(drop=True) #open and read files
    return df

def read_cell_anal_path(path, sep="\t"):
    """read cell data files

    Args:
        path (str): path to cell files
        sep (str, optional): delimiter of files. Defaults to "\t".

    Returns:
        pandas dataframe: dataframe of cell data
    """
    df = pd.concat([read_and_file_stamp(path, f, (i*-1)-1, cell_file=True) 
        for i, f in enumerate(os.listdir(path))]
        ).reset_index(drop=True) #open and read files
    return df

def read_and_file_stamp(path, f, init_group, sep="\t", skel_file=False, cell_file=False):
    """read a file and include it's file name as a column

    Args:
        path (str): path to file
        f (str): filename
        init_group (int): initial default analysis grouping
        sep (str, optional): file str delimiter. Defaults to "\t".
        skel_file (bool, optional): whether a skeleton file is being loaded. Defaults to False.
        cell_file (bool, optional): whether a cell file is being loaded. Defaults to False.

    Returns:
        pandas dataframe: dataframe of data
    """
    if skel_file:
        df = read_skel_file(path, f)
    elif cell_file:
        df = read_cell_file(path, f)
    else:
        df = pd.read_csv(os.path.join(path, f), sep=sep)
        df.loc[:, 'file'] = f[:-4]
    df.loc[:,'analysis_group'] = init_group #default to negative range to reduce the risk of regrouping errors
    return df

def read_skel_file(path, f, sep="\t"):
    """read a skeleton file

    Args:
        path (str): path to file
        f (str): filename
        sep (str, optional): file str delimiter. Defaults to "\t".

    Returns:
        pandas dataframe: dataframe of data
    """
    df = pd.read_csv(os.path.join(path, f), sep=sep)
    fname = f.split("_")[0]
    df.loc[:, 'TotalBranchLength'] = df['# Branches'].values * df['Average Branch Length']
    df = df.sum(axis=0)
    df = df.to_frame().T
    df.loc[:, 'file'] = fname
    cols = np.setdiff1d(df.columns.values, np.array(['Average Branch Length'])) #remove average branch length from columns to reduce username confusion
    return df[cols]

def is_skel_file(file):
    """determines whether a file is the correct skeleton file to read

    Args:
        file (str): filename

    Returns:
        boolean: read file or not
    """
    skel_file=False
    if "rawInfo" in file:
        skel_file=True
    return skel_file

def read_cell_file(path, f, sep="\t", xy=['X', 'Y']):
    """reads and processes a cell file
    Args:
        path (str): path to file
        f (str): filename
        sep (str, optional): file str delimiter. Defaults to "\t".
        xy (list, optional): coordinates to determine the nearest neighbout distance. Defaults to ['X', 'Y'].

    Returns:
        pandas dataframe: dataframe of data
    """
    df = pd.read_csv(os.path.join(path, f), sep=sep)
    nnd_df = construct_nnd_df(df, xy=xy)
    cell_counts = df.shape[0]
    df = pd.merge(df, nnd_df, on=xy, how='left')
    df = df.sum(axis=0)
    df = df.to_frame().T
    df.loc[:, 'cell_counts'] = cell_counts
    df.loc[:, 'file'] = f[:-4]
    return df
