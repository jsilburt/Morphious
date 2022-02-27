# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 16:31:14 2021

@author: joey_
"""

from sklearn.model_selection import ParameterGrid
from datetime import datetime
import pandas as pd
import numpy as np
import time

import morphious_cluster


def setup_grid_ranges(gamma_range=[0.05,0.15,3],nu_range=[0.08,0.2,6],minN_range=[10,24,7]):
    '''
    generates a dataframe of grid search parameters to iterate over.

    Parameters
    ----------
    gamma_range : list-like, optional
        range for ocSVM gamma parameter; indicates the start value, the end-value (inclusive), and the number of total values in the range. The default is [0.05,0.15,3].
    nu_range : list-like, optional
        range for ocSVM nu parameter; indicates the start value, the end-value (inclusive), and the number of total values in the range. The default is [0.08,0.2,6].
    minN_range : list-like, optional
        range for DBSCAN min parameter; indicates the start value, the end-value (inclusive), and the number of total values in the range. The default is [10,24,7].

    Returns
    -------
    param_df : pandas dataframe
        dataframe of grid search parameters.

    '''
    
    gammas = np.linspace(gamma_range[0],gamma_range[1],gamma_range[2])
    nus = np.linspace(nu_range[0],nu_range[1],nu_range[2])
    minNs = np.linspace(minN_range[0],minN_range[1],minN_range[2])
    
    #order gammas > nus > minNs > nfeats 
    param_grid = {'nu' : np.around(nus,decimals=2),
             'minN' : np.around(minNs,decimals=0),
             'gamma' : np.around(gammas, decimals=2)}
    
    param_df = pd.DataFrame(list(ParameterGrid(param_grid)), columns=param_grid.keys())
    return param_df


def grid_search_one_model(train, test, features=[],
                          kernel='rbf', gamma_range=[0.05,0.15,3],nu_range=[0.08,0.2,6], minN_range=[10,26,7],
                          eps = 128, pca=False, nPCs = 3, scale='standard',
                          cross_validate_one_group=False, CVs=5,
                          focal_cluster=False,focal_minN=5,focal_feature="IntDen",
                          summarize_clusters=True, groupby = ['file'], summary_keys=['gamma','nu','minN'], 
                          summary_clusters=['proximal_clusters']):
    '''
    Iteratively applies MORPHIOUS at varying hyper parameters to identify optimal parameters.
    either the training dataset can undergo cross-validation. Alternatively can be used to identify parameters
    which maximize cluster sizes in the test dataset.

    Parameters
    ----------
    train : pandas dataframe
        dataframe containing samples and features.
    test : pandas dataframe
        dataframe containing samples and features, or, None.
    features : list-like, optional
        features to be used in the ocSVM. The default is [].
    kernel : String, optional
        kernel function of the ocSVM. The default is 'rbf'.
    gamma_range : list-like, optional
        range for ocSVM gamma parameter; indicates the start value, the end-value (inclusive), and the number of total values in the range. The default is [0.05,0.15,3].
    nu_range : list-like, optional
        range for ocSVM nu parameter; indicates the start value, the end-value (inclusive), and the number of total values in the range. The default is [0.08,0.2,6].
    minN_range : list-like, optional
        range for DBSCAN min parameter; indicates the start value, the end-value (inclusive), and the number of total values in the range. The default is [10,24,7].
    eps : float, optional
        DBSCAN parameter corresponding to the distance between neighbouring datapoints for establishing a cluster, recommended to be the length of the long diagonal of a feature grid. The default is 128.
    pca : boolean, optional
        PCA transform the features based on the training set. The default is False.
    nPCs : int, optional
        number of principle components to use. The default is 3.
    scale : String, optional
        type of scaling to be applied to the features, choices are standard or minmax. The default is 'standard'.
    cross_validate_one_group : boolean, optional
        Perform cross validation on the training dataset, test set is ignored. The default is False.
    CVs : int, optional
        number of cross-validations. The default is 5.
    focal_cluster : boolean, optional
        whether to use focal clustering. The default is False.
    focal_minN : int, optional
        minimum number of outliers for identifying a cluster. The default is 5.
    focal_feature : String, optional
        feature for identifying focal clusters. The default is "IntDen".
    summarize_clusters : boolean, optional
        summarizes cluster sizes for a given set of parameters to save space. The default is True.
    groupby : list-like, optional
        indeces by which to identify individual images/samples. The default is ['file'].
    summary_keys : list-like, optional
        grid parameters to summarize over. The default is ['gamma','nu','minN'].
    summary_clusters : list-like, optional
        clusters to be summarized. The default is ['proximal_clusters'].

    Returns
    -------
    pandas dataframe
        dataframe of grid parameters and resulting clusters.

    '''
    
    
    print('... setting up grid ranges ...')
    
    #summary_keys = summary_keys + groupby
    
    grids = setup_grid_ranges(gamma_range = gamma_range, nu_range=nu_range, minN_range = minN_range)
    
    grids.loc[:,'cluster_size'] = 0
    grids.loc[:,'num_outliers'] = 0
    
    iterations = 0
    num_iterations = len(grids)
    print(f"----- number of iterations: {num_iterations} -----")
    
    clusters = []
    
    print(grids)

    grids = grids.set_index(summary_keys)
    count_round=0
    for indexes, df in grids.groupby(level=summary_keys):
        st = time.time()
        g = indexes[0]
        n = indexes[1]
        m = indexes[2]
        
        print(f"gamma: {g}, nu: {n}, minN: {m}")
         
        if cross_validate_one_group:
            clust = morphious_cluster.iter_all_one_model(train, test, features=features,extra_scalers=[],
                               cross_validate_one_group=cross_validate_one_group, CVs = CVs,scale=scale,
                               gamma=g, nu=n, kernel='rbf', minN=int(m), eps=eps,
                               focal_cluster=False,focal_minN=5,focal_feature="IntDen",
                               pca=pca,n_comps=nPCs,return_pca_model=False,
                              relabel_clusters=True, combine=False, label_unclustered=False, unclustered_reference='proximal_clusters',
                              groupby=['file'])
            
        else:
            x, clust = morphious_cluster.iter_all_one_model(train, test, features=features,extra_scalers=[],
                               cross_validate_one_group=cross_validate_one_group, CVs = CVs,scale=scale,
                               gamma=g, nu=n, kernel='rbf', minN=int(m), eps=eps,
                               focal_cluster=False,focal_minN=5,focal_feature="IntDen",
                               pca=pca,n_comps=nPCs,return_pca_model=False,
                              relabel_clusters=True, combine=False, label_unclustered=False, unclustered_reference='proximal_clusters',
                              groupby=['file'])
        
        clust.loc[:,'gamma'] = g
        clust.loc[:,'nu'] = n
        clust.loc[:,'minN'] = m

        
        if summarize_clusters:
            #print("--- summarizing ---")
            clust = summarize_cluster_grids(clust, keys=summary_keys+groupby, cluster_types=summary_clusters)
        clusters.append(clust)
        
        iterations += 1
        if (iterations % 50) == 0:
            print(f"progress.. {iterations}/{num_iterations}")
        #print(f"===== TIME FOR ITERATION {time.time()-st} -- #{count_round}/{num_iterations} =====")
        count_round += 1
    return pd.concat(clusters)

def summarize_cluster_grids(clusters,keys=['gamma','nu','min','file'],
                            cluster_types=['proximal_clusters']):
    '''
    summarizes the magnitude of clustering for a given image and set of hyper-parameter

    Parameters
    ----------
    clusters : pandas dataframe
        dataframe with clusters.
    keys : list-like, optional
        Indeces to summarize over. The default is ['gamma','nu','min','file'].
    cluster_types : list-like, optional
        cluster columns to summarize. The default is ['proximal_clusters'].

    Returns
    -------
    summary : pandas dataframe
        summarized cluster files.

    '''
    nClusts = {}
    for cl in cluster_types:
        nClusts[cl] = len(np.unique(clusters.loc[clusters[cl]>-1,cl]))
        clusters.loc[clusters[cl]>-1,cl] = 1
        clusters.loc[clusters[cl]==-1,cl] = 0
    #'''
    summary = clusters[keys+cluster_types]
    
    #summary = summary.loc[summary['proximal_clusters']>-1]
    summary = summary.groupby(keys)[cluster_types].agg(['sum','count'])
    summary.columns = summary.columns.map(''.join)
    for cl in nClusts.keys():
        summary.loc[:,cl+"_nclusts"] = nClusts[cl]
    for cl in cluster_types:
        summary.loc[:,cl+'_perc_cluster'] = summary[cl+'sum'] / summary[cl+'count']
    return summary



def resummarize_cluster_grids(clusters,keys=['gamma','nu','min'], cols_to_summarize=['proximal_clusterssum','proximal_clusterscount'], cluster_types=['proximal_clusters']):
    '''
    summarizes grids to eliminate the file index and calculate percentage of clusters present for each iteration of hyper-parameters

    Parameters
    ----------
    clusters : pandas dataframe
        dataframe containing the hyper-parameter search and the resulting clusters.
    keys : list-like, optional
        columns to summarize over. The default is ['gamma','nu','min'].
    cols_to_summarize : list-like, optional
        input columns to further summarize. The default is ['proximal_clusterssum','proximal_clusterscount'].
    cluster_types : list-like, optional
        cluster columns to summarize. The default is ['proximal_clusters'].

    Returns
    -------
    summary : TYPE
        DESCRIPTION.

    '''
    summary = clusters.groupby(keys)[cols_to_summarize].sum()
    for cl in cluster_types:
        summary.loc[:,cl+'_perc_cluster'] = summary[cl+'sum'] / summary[cl+'count']
    return summary


def round_parameters(cluster, cols=['gamma','nu']):
    '''
    rounds parameters to 2 decimal places

    Parameters
    ----------
    cluster : pandas dataframe
        dataframe with hyper-parameter and cluster columns.
    cols : list-like, optional
        columns to round. The default is ['gamma','nu'].

    Returns
    -------
    cluster : pandas dataframe
        dataframe with rounded columns.

    '''
    for col in cols:
        cluster.loc[:,col] = np.around(cluster[col].values, decimals=2)
    return cluster

   
def find_best_parameters(untr, trt, keys=['gamma','nu','minN'], cluster_metric='proximal_clusterssum'):
    '''
    matches a grid-search of cross-validation with the training set with a grid-search of the test set 
    to find the set of hyperparameters which yeilds no clusters in the training set, and maximizes the
    magnitudes of clusters in the test set.

    Parameters
    ----------
    untr : pandas dataframe
        grid search results from a grid search of the training set (via cross-validation).
    trt : pandas dataframe
        grid search results from a grid search of the test set.
    keys : list-like, optional
        hyper-parameters to find optimal values. The default is ['gamma','nu','minN'].
    cluster_metric : String, optional
        metric to search for cluster sizes. The default is 'proximal_clusterssum'.

    Returns
    -------
    top : TYPE
        DESCRIPTION.

    '''
    untr = round_parameters(untr.reset_index())
    trt = round_parameters(trt.reset_index())
    
    untr = untr.set_index(keys)
    trt = trt.set_index(keys)
    
    candidate_params = untr.loc[untr[cluster_metric]==0]
    
    top = trt.loc[candidate_params.index,cluster_metric]
    top = top.sort_values(ascending=False)
    return top
    
def save_grids(grid, path, cv=False, nCVs = 5):
    '''
    save grid search dataframe to file

    Parameters
    ----------
    grid : pandas dataframe
        results of a grid search.
    path : String
        output path to save to.
    cv : boolean, optional
        whether the dataframe is a cross-validation grid search; used for specifying in the file name. The default is False.
    nCVs : int, optional
        the number of cross-validations, used for specifying in the file name. The default is 5.

    Returns
    -------
    None.

    '''
    curr_time = datetime.now()
    
    dt_string = curr_time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    file = dt_string
    if cv:
        file = file + f"_{nCVs}-fold-CV_"
    else:
        file = file + "_test-dataset_"
    file = file+"_paramater_grid_raw.csv"
    grid.to_csv(path+"/"+file)
    