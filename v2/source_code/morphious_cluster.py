# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 22:05:13 2020

@author: joey_
"""
import pandas as pd
import numpy as np
import math
import time
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn import svm
from sklearn.cluster import DBSCAN
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold


#import warnings
#warnings.filterwarnings('error')

def standard_scale(train, test, features=["Mean","IntDen","Area"],
                   dropna=True,newcols=True, scale='standard'):
    '''
    normalizes/scales features from training and test dataframes

    Parameters
    ----------
    train : pandas dataframe
        dataframe of features used for training
    test : pandas dataframe
        dataframe of features used for testing
    features : List-like of features, optional
        specify the set of features which will be scalled. The default is ["Mean","IntDen","Area"].
    dropna : boolean, optional
        specifies that missing cases will be dropped. The default is True.
    newcols : boolean, optional
        will save scaled features in new columns, unscaled columns will be denoted as [feature]_raw. The default is True.
    scale : string, optional
        choices are standard or minmax. The default is 'standard'.

    Returns
    -------
    train : pandas dataframe
        dataframe scaled based on train df features.
    test : pandas dataframe
        dataframe scaled based on train df features.

    '''
    if newcols:
        for f in features:
            newFeat = f+"_raw"
            train.loc[:,newFeat] = train.loc[:,f]
            if test is not None:
                test.loc[:,newFeat] = test.loc[:,f]
    
    if dropna:
        train = train.dropna(subset=features)
        if test is not None:
            test = test.dropna(subset=features)

    if scale == 'standard':
        scaler = StandardScaler()
    elif scale == 'minmax':
        scaler = MinMaxScaler()
    
    scaler.fit(train.loc[:, features])
    train.loc[:,features] = scaler.transform(train.loc[:, features])
    if test is not None:
        test.loc[:,features]=scaler.transform(test.loc[:, features])
    return train, test

def trim(X,feature="Mean",gt=True,threshold=-1):
    '''
    thresholds a dataframe based on a feature and a standardized value
    
    Parameters
    ----------
    X : pandas dataframe
        df to be trimmed
    feature : String, optional
        the feature selected for thresholding. The default is "Mean".
    gt : boolean, optional
        threshold greater than (true) or less than (false) the threshold value. The default is True.
    threshold : float, optional
        the threshold value. The default is -1, i.e., 1 SD below the mean after standard scaling.

    Returns
    -------
    re : pandas dataframe
        a dataframe thresholded based on the selected criteria.

    '''
    if gt:
        re = X.loc[X[feature] > threshold]
    else:
        re = X.loc[X[feature] < threshold]
    return re

def dbscan_cluster(data,features=["BX","BY"], minN=20, eps=None, label="proximal_clusters", return_labels=False,boxsize=150):
    '''
    uses a DBSCAN classifier to identify density based clusters

    Parameters
    ----------
    data : pandas dataframe
        input dataframe to be clustered.
    features : list-like, optional
        features to use for density clustering. The default is ["BX","BY"].
    minN : int, optional
        the minimum number of neighbours in the distance eps to define a cluster. The default is 20.
    eps : float, optional
        distance for the number of neighbours to define a cluster. if None, the distance is calculated as the hypotenuse of a boxsize x boxsize triangle. The default is None.
    label : String, optional
        column label to store cluster labels as. The default is "proximal_clusters".
    return_labels : boolean, optional
        if true, returns just a list of clusters, instead of a dataframe. The default is False.
    boxsize : float, optional
        the grid size used for generating the feature map. The default is 150.

    Returns
    -------
    result : pandas dataframe, or, numpy array
        either the dataframe with identified clusters embedded as a column, or the columns values, as returned as a numpy array.

    '''
    if eps == None:
        eps = math.sqrt((2.0*(boxsize/1.5)**2)) + 1

    print('minN: ',minN, 'epsilon: ',eps)
    clusterer=DBSCAN(min_samples=minN,eps=eps)
    clusters = clusterer.fit_predict(data[features])
    if return_labels:
        result = clusters
    else:
        data.loc[:,label] = clusters
        result = data
    return result

def process_focal_cluster(df,focal_minN=5,focal_feature="IntDen",focal_thresh=None,return_thresh=False, 
                          subsetby="proximal_clusters", eps=None):
    '''
    function to identify focal clusters by applying DBSCAN to proximal clusters / outliers which are first thresholded by a cutoff value.
    This cutoff value can be automatically determined by setting focal_thresh to None

    Parameters
    ----------
    df : pandas dataframe
        dataframe of features and coordinates for identifying focal clusters.
    focal_minN : int, optional
        minimum number of neighbours to identify a DBSCAN cluster. The default is 5.
    focal_feature : String, optional
        feature by which a threshold is established for identifying focal grid candidates to be subsequently clustered. The default is "IntDen".
    focal_thresh : float, optional
        A predefined threshold for evaluating a threshold value for identifying putative focal grid candidates. If None, a threshold value is calculated automatically (recommended). The default is None.
    return_thresh : boolean, optional
        return the threshold value or not. The default is False.
    subsetby : String, optional
        Either "outliers" or "proximal_clusters", the base set of . The default is "proximal_clusters".

    Returns
    -------
    re : pandas dataframe
        returns a pandas dataframe with focal clusters embedded as a column.

    '''
    if focal_thresh == None:
        focal_thresh = get_focal_threshold(df,feature=focal_feature,subsetby=subsetby)
    print("focal threshold: ", focal_thresh)
    trt_f = trim(df,feature=focal_feature,gt=True,threshold=focal_thresh)
    if len(trt_f) > 0:
        df.loc[trt_f.index, "focal_clusters"] = dbscan_cluster(trt_f,minN=focal_minN,return_labels=True, eps=eps)
        df.loc[:,"focal_clusters"] = df["focal_clusters"].fillna(-1)
    else:
        df.loc[:,"focal_clusters"] = -1
    if return_thresh:
        re = [df,focal_thresh]
    else:
        re = df
    return re

def get_focal_threshold(data,feature="IntDen",subsetby="proximal_clusters",default_threshold=99):
    '''
    Finds a focal threshold value. A feature array is sorted in ascending order, 
    and the threshold is determined as the elbow point of thre resultant curve.

    Parameters
    ----------
    data : pandas dataframe
        the data which contains the specified feature.
    feature : String, optional
        the feature used to evaluate a threshold. The default is "IntDen".
    subsetby : String, optional
        Either 'proximal_clusters', or 'outlier', specifies a subset by which the focal feature is sorted for evaluating the threshold. The default is "proximal_clusters".
    default_threshold : int, optional
        an arbitrarily large value the threshold is assigned if a threshold is not identified. Will result in no focal clusters found. The default is 99.

    Returns
    -------
    threshold : float
        a threshold value determined for the specified feature.

    '''
    threshold = default_threshold
    x = data
    if subsetby == "outlier":
        x = data.loc[data["outlier"] == -1]
    elif subsetby == "proximal_clusters":
        x = data.loc[data["proximal_clusters"]>-1]
    if len(x) > 0:
        x = x[feature].sort_values(ascending=True)
        threshold = scan_elbow(x,default_threshold=default_threshold)
    return threshold

def find_elbow(curve):
    '''
    Finds the elbow point of a curve used for to determining a threshold value.
    The elbow point is determined by first drawing a vector connecting the first and last points of the curve.
    From this vector, perpendicular vectors that connect this vector to each data point in the curve are evaluated.
    The elbow point is determined as the data point corresponding to the largest perpendicular vector.
    

    Parameters
    ----------
    curve : list-like
        values sorted in ascending order for which the elbow of the curve is identified.

    Returns
    -------
    idxOfBestPoint : int
        the index of the elbow point.
    float
        the value of the elbow point, corresponding to the threshold value.
    float
        the magnitude of the elbow point perpendicular vector.

    '''
    nPoints = len(curve)
    #print(curve)
    allCoord = np.vstack((range(nPoints), curve)).T
    np.array([range(nPoints), curve])
    firstPoint = allCoord[0]
    lineVec = allCoord[-1] - allCoord[0] # draw a line between last point and first point
    if np.sqrt(np.sum(lineVec**2)) > 0:
        lineVecNorm = lineVec / np.sqrt(np.sum(lineVec**2))   #find the normal
        vecFromFirst = allCoord - firstPoint #draw lines from all points to the first point
        scalarProduct = np.sum(vecFromFirst * np.matlib.repmat(lineVecNorm, nPoints, 1), axis=1)
        vecFromFirstParallel = np.outer(scalarProduct, lineVecNorm)
        distFromFirstParallel = np.sqrt(np.sum(vecFromFirstParallel ** 2, axis=1))
        vecToLine = vecFromFirst - vecFromFirstParallel
        distToLine = np.sqrt(np.sum(vecToLine ** 2, axis=1))
        idxOfBestPoint = np.argmax(distToLine)
        #angle = np.arctan(distToLine[idxOfBestPoint]/distFromFirstParallel[idxOfBestPoint])
        #print("elbow point: %s, parallel dist: %s, perpendicular dist: %s, angle: %s" %(idxOfBestPoint,distFromFirstParallel[idxOfBestPoint],distToLine[idxOfBestPoint],angle))
        return idxOfBestPoint,curve[idxOfBestPoint],distToLine[idxOfBestPoint]
    else:
        return -1, -1, 0 #these values will be ignored by the output

def scan_elbow(curve,penalty=0.05,min_curve_distance=0.5,default_threshold=99):
    '''
    Iteratively shortens the curve and evaluates the focal threshold (i.e. the elbow point of the curve).
    The focal threshold is determined as the modal elbow point from this procedure.

    Parameters
    ----------
    curve : list-like
        values sorted in ascending order from which the elbow of the curve is identified.
    penalty : float, optional
        the proportion of the curve that is removed upon each iteration. The default is 0.05.
    min_curve_distance : float, optional
        a minimum curve distance to ensure that the curve is sufficiently curved (i.e., not a straight line). The default is 0.5.
    default_threshold : float, optional
        value returned if no elbow point for the curve is found. The default is 99.

    Returns
    -------
    thresh : float
        threshold value for evaluating putative focal clusters.

    '''
    sub = int(penalty * len(curve))
    if sub == 0:
        sub = 1
    nIters = int(len(curve)/sub)
    elbows = []
    elbow_distance = []
    for i in range(0,nIters):
        start = sub*i
        elbow = find_elbow(curve.iloc[start:].values)
        elbows.append(elbow[1])
        elbow_distance.append(elbow[2])
        #print(elbow)
    thresh = stats.mode(elbows).mode[0]
    threshindex = np.where(elbows==thresh)[0][0] # get first index where mode elbow point i.e. threshold value is reached.
    #print("elbow dist is: ", elbow_distance[threshindex])
    if(elbow_distance[threshindex] < min_curve_distance): # assess curvature at this point
        #print(elbow_distance[threshindex])
        thresh = default_threshold
    return thresh


       
def iter_clustering_one_model(train, test_series, features = ['IntDen','Mean','D'], 
                              groupby=['file'], coords=['BX','BY'],
                    gamma=0.1, nu=0.1, kernel='rbf', minN=20,eps=None,
                                  trim_feature='Mean', trim_threshold=-1,
                                  focal_cluster=False, focal_feature='IntDen', focal_minN=5, boxsize=150
                   ):
    '''
    Trains a one-class support vector machine (ocSVM) with training data, and subsequently tests in on test data.
    DBSCAN is subsequently applied to identified outliers to find 'proximal clusters'
    Focal clusters are further identified as a particular subset of proximal clusters which correspond to
    those clusters which show the strongest outlier features. Focal clusters are found by first
    thresholding proximal clusters by a defined feature (e.g., IntDen). DBSCAN is applied to these candidate
    data points to identify focal clusters. ocSVM and DBSCAN are based on the implementations via Sci-kit-learn

    Parameters
    ----------
    train : pandas dataframe
        training data set.
    test_series : pandas dataframe
        test data set.
    features : list-like, optional
        features used for the ocSVM classification. The default is ['IntDen','Mean','D'].
    groupby : list-like, optional
        columns used to distinguish unique image samples. The default is ['file'].
    coords : list-like, optional
        variables to define the xy coordinates of individual grid points. The default is ['BX','BY'].
    gamma : float, optional
        gamma hyper-parameter for the ocSVM; 
        used for tuning the kernel function and impacts model complexity. The default is 0.1.
    nu : float, optional
        nu hyper-prarmeter for the ocSVM; 
        proportional to the misclassification rate and regulates model complecity. The default is 0.1.
    kernel : String, optional
        kernel function for the ocSVM. The default is 'rbf'.
    minN : int, optional
        min hyper-parameter for DBSCAN; 
        corresponds to the minimum number of neighours within distance eps. The default is 20.
    eps : float, optional
        eps hyper-parameter for DBSCAN;
        see above; if None, the eps is calculated as the hypotenuse of a boxsize x boxsize triangle. The default is None.
    trim_feature : String, optional
        selected feature to loosely threshold outliers to ensure they reflect activated cells, and not low signal artifacts. The default is 'Mean'.
    trim_threshold : float, optional
        a threshold value for the trim_feature (see above). The default is -1.
    focal_cluster : boolean, optional
        if true, finds focal clusters. The default is False.
    focal_feature : String, optional
        feature corresponding to most activated grids used to identify focal clusters. The default is 'IntDen'.
    focal_minN : int, optional
        min hyper-parameter for DBSCAN; 
        corresponds to the minimum number of neighours within distance eps to identify focal clusters. The default is 5.
    boxsize : int, optional
        the selected grid size used when extracting features. The default is 150.

    Returns
    -------
    pandas dataframe
        contains outlier and clusters as columns.

    '''
    
    proximal_cluster_label="proximal_clusters"
    
    st = time.time()
    grouping_keys = ['ID','Section']
    test_series = test_series.set_index(groupby+['boxID'])
    test_sections = []
    
    clusterer = DBSCAN(min_samples=minN,eps=eps)
    
    st = time.time()
    classifier = svm.OneClassSVM(nu=nu,gamma=gamma,kernel=kernel)
    classifier.fit(train[features])
    print(f" fit time: {time.time()-st}")

    for groups, section in test_series.groupby(level=groupby):
        section = section.copy() #remove settingwithcopy warning
        outliers = classifier.predict(section[features])
        section.loc[:,"outlier"] = outliers
        #outliers can e.g., of activated cells, or underexposed tissue regions
        #therefore this step conducts a minimal degree of thresholding (default: mean - 1SD) to ensure outliers indicate activated cells
        to_cluster = section.loc[((section["outlier"]==-1) & (section[trim_feature]>trim_threshold))] 
        if len(to_cluster)>0:
            clusters = clusterer.fit_predict(to_cluster[coords])
            section.loc[to_cluster.index, proximal_cluster_label] = clusters
            if focal_cluster:
                section = process_focal_cluster(section, focal_feature=focal_feature, focal_minN=focal_minN, eps=eps)
        test_sections.append(section)
        
    return pd.concat(test_sections).reset_index()
    
                    
    
def iter_all_one_model(train, test, features=["Mean","IntDen","D"],extra_scalers=["IntDen"],
                           cross_validate_one_group=False, CVs = 5,
                       scale='standard',
                           gamma=0.1, nu=0.1, kernel='rbf', minN=20, eps=128,
                           focal_cluster=False,focal_minN=5,focal_feature="IntDen",
                           pca=False,n_comps=3,return_pca_model=False,
                          relabel_clusters=True, combine=False, label_unclustered=True, unclustered_reference='proximal_clusters',
                          groupby=['file'],
                          coords = ['BX','BY'],
                          ):
    '''
    all in one convenience function to perform scaling, PCA transformation, and MORPHIOUS clustering. 
    Is used both to perform cross validation of the training set, or to perform operations on the test dataframe

    Parameters
    ----------
    train : pandas dataframe
        training data set.
    test : pandas dataframe
        test data set or None.
    features : : list-like, optional
        features used for the ocSVM classification. The default is ['IntDen','Mean','D'].
    extra_scalers : list-like, optional
        option to choose additional features to be scaled. The default is ["IntDen"].
    cross_validate_one_group : boolean, optional
        if true, performs cross-validation on the train dataset, the test dataset is ignored. The default is False.
    CVs : int, optional
        the number of cross-validations to be performed. The default is 5.
    scale : String, optional
        method for scaling the data, choices are 'standard' or 'minmax'; scaling is based on the training set and applied to the test set. The default is 'standard'.
    gamma : float, optional
        gamma hyper-parameter for the ocSVM; 
        used for tuning the kernel function and impacts model complexity. The default is 0.1.
    nu : float, optional
        nu hyper-prarmeter for the ocSVM; 
        proportional to the misclassification rate and regulates model complecity. The default is 0.1.
    kernel : String, optional
        kernel function for the ocSVM. The default is 'rbf'.
    minN : int, optional
        min hyper-parameter for DBSCAN; 
        corresponds to the minimum number of neighours within distance eps. The default is 20.
    eps : float, optional
        eps hyper-parameter for DBSCAN;
        see above; if None, the eps is calculated as the hypotenuse of a boxsize x boxsize triangle. The default is None.
    focal_cluster : boolean, optional
        if true, finds focal clusters. The default is False.
    focal_feature : String, optional
        feature corresponding to most activated grids used to identify focal clusters. The default is 'IntDen'.
    focal_minN : int, optional
        min hyper-parameter for DBSCAN; 
        corresponds to the minimum number of neighours within distance eps to identify focal clusters. The default is 5.
    pca : boolean, optional
        uses PCA to transform selected features. PCA is trained on the train set and applied to the test set. The default is False.
    n_comps : int, optional
        number of principle components to include as features. The default is 3.
    return_pca_model : boolean, optional
        returns the pca model object. The default is False.
    relabel_clusters : boolean, optional
        re-labels all clusters to 1, regardless of which cluster they are part of. Is applied seperately to proximal and focal clusters. The default is True.
    combine : boolean, optional
        combines proximal and focal clusters into combined clusters which are assigned to a new column. The default is False.
    label_unclustered : boolean, optional
        adds a column to identify grids which did not have a cluster. The default is True.
    unclustered_reference : String, optional
        the reference point to evaluate whether a grid is unclustered, changes to 'combined_clusters' if focal clusters are identified. The default is 'proximal_clusters'.
    groupby : list-like, optional
        list of features used to identify unique images. The default is ['file'].
    coords : list-like, optional
        list of features defining the spatial coordinates. The default is ['BX','BY'].

    Returns
    -------
    pandas dataframe
        returns the training dataframe, if the test dataframe is not None, it is also returned

    '''

    cluster_cols = []
    input_features = features
    to_scale_feats = features + extra_scalers
    if focal_cluster:
        to_scale_feats = to_scale_feats + [focal_feature]
        
    to_scale_feats = np.unique(np.array(to_scale_feats))
    train, test = standard_scale(train,test,features=to_scale_feats,dropna=True,newcols=True, scale=scale)
        
    if pca:
        if test is not None:
            input_features, train, test = pca_transform_features(train, test, features, n_comps, only_model=False)
        else:
            input_features, train = pca_transform_features(train, test, features, n_comps, only_model=False)
    
    if cross_validate_one_group:
        
        series = train
        all_series=[]
            
        kf = KFold(n_splits=CVs, shuffle=True, random_state=42)
        series = series.set_index(groupby)
        indexes = series.index.unique()
        for train_index, test_index in kf.split(indexes):
            
            X_train, X_test = series.loc[indexes[train_index]], series.loc[indexes[test_index]]
            
            test_sections = iter_clustering_one_model(X_train.reset_index(), X_test.reset_index(), coords=coords,
                                                      features=input_features, gamma=gamma, nu=nu, kernel=kernel, 
                                                      minN=minN,eps=eps,groupby=groupby,
                                                     focal_cluster=focal_cluster, focal_feature=focal_feature, focal_minN=focal_minN
                                                    )
            all_series.append(test_sections)
        train = pd.concat(all_series, sort=True)
        cluster_cols.append('outlier')
        cluster_cols.append('proximal_clusters')
    
    else:
        test = iter_clustering_one_model(train, test, features=input_features, coords=coords,
                                                gamma=gamma, nu=nu, kernel=kernel,minN=minN,eps=eps,groupby=groupby,
                                               focal_cluster=focal_cluster, focal_feature=focal_feature, focal_minN=focal_minN)
        #'''
        train.loc[:, 'proximal_clusters'] = np.nan
        if focal_cluster:
            train.loc[:, 'focal_clusters'] = np.nan
        #'''
        cluster_cols.append('outlier')
        cluster_cols.append('proximal_clusters')
        if focal_cluster:
            cluster_cols.append('focal_clusters')
    if relabel_clusters:
        relabel = ['proximal_clusters']
        if focal_cluster:
            relabel = relabel+['focal_clusters']
        train = relabel_clusters2(train, clusters=relabel)
        if test is not None:
            test = relabel_clusters2(test, clusters=relabel)
        
    if combine:
        train = combine_clusters(train)
        if test is not None:
            test = combine_clusters(test)
            
        unclustered_reference="combined_clusters"
        cluster_cols.append("combined_clusters")
    
    if label_unclustered:
        train = assign_unclustered(train, cluster=unclustered_reference)
        if test is not None:
            test = assign_unclustered(test, cluster=unclustered_reference)
        cluster_cols.append("unclustered")
        
    selected_cols = np.array(features+input_features+extra_scalers+groupby+cluster_cols+coords)
    selected_cols = np.intersect1d(train.columns.values, selected_cols)
    
    train = train.loc[:,selected_cols]
    if test is not None:
        test = test.loc[:,selected_cols]
        return train, test
    else:
        return train

def pca_transform_features(train, test, features, n_comps, only_model=False):
    '''
    uses the training dataset to construct a PCA model which is applied to the
    training and test datasets.

    Parameters
    ----------
    train : pandas dataframe
        the training dataset.
    test : pandas dataframe
        the test dataframe or None.
    features : list-like
        features to be PCA transformed.
    n_comps : int
        number of principle components to be extracted.
    only_model : boolean, optional
        returns only the trained model. The default is False.

    Returns
    -------
    pandas dataframe
        returns a dataframe with principle components added as new columns.

    '''
    to_return = []
    pca_model=PCA(n_components=n_comps).fit(train[features])
    
    if only_model:
        print(pca_model.explained_variance_ratio_, 'explains: ',pca_model.explained_variance_ratio_.sum())
        return pca_model
    else:
        train = assign_components(train, pca_model.transform(train[features]))
        c = np.array(['pca_']*n_comps)
        pca_features = list(np.core.defchararray.add(c, np.arange(n_comps).astype(str)))
        to_return.append(pca_features)
        to_return.append(train)
        if test is not None:
            test = assign_components(test, pca_model.transform(test[features]))
            to_return.append(test)
    return to_return
   
def relabel_clusters2(df,clusters=["proximal_clusters","focal_clusters"]):
    '''
    binarizes cluster groups to be either 1 i.e., part of a cluster, or -1, no cluster

    Parameters
    ----------
    df : pandas dataframe
        dataframe containing cluster columns to be relabelled.
    clusters : list-like, optional
        contains the names of columns for which the clusters are to be relabelled. The default is ["proximal_clusters","focal_clusters"].

    Returns
    -------
    df : pandas dataframe
        dataframe with cluster columns relabelled.

    '''
    df = df.reset_index(drop=True)
    for cl in clusters:
        f = lambda x: 1 if x > -1 else -1
        df.loc[:,cl] = df[cl].apply(f)
    return df
    #return df
'''
def col_to_numeric(df,col):
    if type(col) is list:
        for c in col:
            df.loc[:,c]= pd.to_numeric(df[c])
    else:
        df.loc[:,col]= pd.to_numeric(df[col])
    return df
'''

def get_numeric_cols(df):
    '''
    returns numeric columns in a dataframe

    Parameters
    ----------
    df : pandas dataframe
        dataframe to get numeric columns from.

    Returns
    -------
    pandas dataframe
        pandas dataframe with only numeric columns.

    '''
    return df.select_dtypes(include= np.number)


def combine_clusters(df,baseline="proximal_clusters",add="focal_clusters",label="combined_clusters",
                     groupby=['file'], coords=['BX', 'BY']):
    '''
    aggregates two cluster classes types a single merged cluster group

    Parameters
    ----------
    df : pandas dataframe
        dataframe containing the clustering data.
    baseline : String, optional
        the label for the first cluster column to be merged. The default is "proximal_clusters".
    add : String, optional
        the label for the second cluster column to be merged. The default is "focal_clusters".
    label : String, optional
        the name of the resultant merged cluster column. The default is "combined_clusters".
    groupby : list-like, optional
        unique identifiers for which to identify individual images or samples. The default is ['file'].
    coords : list-like, optional
        coordinates corresponding to the spatial locations of grids. The default is ['BX', 'BY'].

    Returns
    -------
    pandas dataframe
        returns a dataframe with the combined clusters column added.

    '''
    df.loc[:,label] = df[baseline]
    df = df.set_index(groupby + coords + ["boxID"])
    for indexes, dat in df.groupby(level=groupby):
        toadd = dat.reset_index().set_index(groupby + coords + ["boxID",baseline,add])
        if 1 in toadd.index.get_level_values(add):
            toadd = toadd.xs((-1,1),level=(baseline,add))
            if len(toadd) > 0:
                df.loc[toadd.index,label] = 1
    return df.reset_index()

def assign_unclustered(df,label="unclustered",cluster="proximal_clusters"):
    '''
    creates a column that labels grids which did not cluster with a 1 and -1 for those which are part of a cluster

    Parameters
    ----------
    df : pandas dataframe
        dataframe of cluster data.
    label : Sting, optional
        label for resultant column. The default is "unclustered".
    cluster : String, optional
        column of clusters to reference when assigning unclustered grids. The default is "proximal_clusters".

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    df.loc[:,label] = df[cluster]*-1
    df.loc[:,label] = df[label].fillna(-1)
    return df

def assign_components(df,pca):
    '''
    includes principle components as columns in the dataframe; labelled as pca_[n]

    Parameters
    ----------
    df : pandas dataframe
        dataframe of data.
    pca : 2D array
        output from pca.transform().

    Returns
    -------
    df : pandas dataframe
        dataframe with pca components added in.

    '''
    for i in range(0,len(pca[0])):
        col="pca_"+str(i)
        df.loc[:,col]=pca[:,i]
    return df




    