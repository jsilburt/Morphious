# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 13:13:12 2021

@author: joey_
"""


import os
from datetime import datetime

def write_cluster_file(df, file, path="", boxsize=150, scale=1.5):
    '''
    writes the coordinates of clusters to a .csv file

    Parameters
    ----------
    df : pandas dataframe
        dataframe containing the clusters and cluster coordinates.
    file : String
        name of output file.
    path : String, optional
        the output path. The default is "".
    boxsize : int, optional
        grid size used for initial feature extraction. The default is 150.
    scale : float, optional
        scale of the pixels in (um/pixel) of initial image. The default is 1.5.

    Returns
    -------
    None.

    '''
    coords = df.loc[:, ['BX','BY']]
    if len(coords) > 0:
        coords.loc[:,'BX'] = coords.loc[:,'BX'] * scale
        coords.loc[:,'BY'] = coords.loc[:,'BY'] * scale
        coords.loc[:,'Boxsize'] = boxsize
        coords.to_csv(path+"/"+file)
        
    
def write_all_cluster_files(df,clusters=["proximal_clusters","focal_clusters"],
                            path="",write_unclustered=True, unclustered_reference = 'combined_clusters', 
                            unclustered_output="unclustered", groupby = ["file"], scale=1.5):
    '''
    writes the coordinates of all cluster types into files. Unclustered samples are written as an empty file.

    Parameters
    ----------
    df : pandas dataframe
        dataframe with clustering data.
    clusters : list-like, optional
        names of clustering columns. The default is ["proximal_clusters","focal_clusters"].
    path : String, optional
        output path for cluster files. The default is "".
    write_unclustered : boolean, optional
        write the name of images without any clusters as empty files. The default is True.
    unclustered_reference : String, optional
        The absence of any clusters of this cluster type indicates the sample has no clusters. The default is 'combined_clusters'.
    unclustered_output : String, optional
        name of a sub directory to write unclustered files. The default is "unclustered".
    groupby : String, optional
        Index to refer to unique samples/images. The default is ["file"].

    Returns
    -------
    None.

    '''
    df = df.set_index(groupby+clusters)
    curr_time = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = curr_time.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    path = path + "/" + dt_string + "/"
    
    unclustered_path = f"{path}/{unclustered_output}/"

    
    print(df.columns.values)
    print(df.head())
    for c in clusters:
        print(c)
        for indexes, dat in df.groupby(level=groupby)[["BX","BY"]]:
            
            #dat = dat.copy() #remove settingwithcopy warning
            if len(groupby) > 1:
                file = "_"
                file = file.join(list(indexes))+".csv"
            else:
                file = indexes+".csv"
            print(file)
            values = dat.index.get_level_values(c)
            if 1 in values:
                x = dat.xs(1, level=c,drop_level=False).copy() #remove settingwithcopy warning
                dest_path = path+"/"+c.replace("_clusters","")
                if check_subdir(dest_path):
                    write_cluster_file(x,file,path=dest_path, scale=scale)
                else:
                    print("Error! path not found")
                    
            else:
                print(indexes, "no clusters")
                if write_unclustered:
                    if c == unclustered_reference:
                        if check_subdir(unclustered_path):
                            with open(unclustered_path+file,'w') as w:
                                print("wrote unclustered")
                                w.write("")
                        else:
                            print("Error! path not found")

                
def check_subdir(path, create_path=True):
    '''
    checks if a sub directory exists and creates one if it does not

    Parameters
    ----------
    path : String
        path to check.
    create_path : boolean, optional
        creates a path if it doesn't exist. The default is True.

    Returns
    -------
    bool
        returns whether the path exists.

    '''
    if not os.path.exists(path):
        if create_path:
            os.makedirs(path)
            return True
        else:
            return False
    else:
        return True
    