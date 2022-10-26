# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 14:43:36 2020

@author: joey_
"""
# from morphious_input import *
# from morphious_gui import *
# from morphious_cluster import *
# from morphious_write_clusters import *
# from morphious_gridsearch import *

import morphious_input
import morphious_gui
import morphious_cluster
import morphious_write_clusters
import morphious_gridsearch
import morphious_analysis

import pandas as pd
import numpy as np
import os

class Controller(object):
    
    def __init__(self):
        '''
        Constructor function for controller object. The controller connectes the GUI
        with the backend code

        Returns
        -------
        None.

        '''
        #loaded datasets
        self.train_df = None #training dataset
        self.test_df = None #test dataset
        
        #cluster results datasets
        self.cv_clusters = None #results of cross validation clustering of the training set
        #self.train_clusters = None #the training dataset after it is used for training, i.e., contains scaled features, but no clusters
        self.test_clusters = None #the results of the test set after clustering
        
        #GUI frames
        self.main_frame = None 
        self.morphious_frame = None 
        self.train_option_frame = None
        self.test_option_frame = None
        self.cluster_frame = None
        self.features_frame = None
        self.focal_feature_frame = None
        self.console_frame = None
        self.grid_search_frame = None
        self.save_frame = None
        self.save_df_frame = None
        self.analysis_selector_frame = None
        self.IF_analysis_frame = None
        self.skel_analysis_frame = None
        
        #paths to feature files
        self.feature_path = None
        self.fractal_path = None
        self.skeleton_path = None
        self.cell_path = None
        self.user_data_path = None
        self.df_path = None
        self.boxsize = None #boxsize used for extracting features
        self.scale = None #scale of the images

        #paths to analysis files + dfs
        self.IF_anal_path = None
        self.skel_anal_path = None
        self.cell_anal_path = None

        self.IF_anal_df = None
        self.skel_anal_df = None
        self.cell_anal_df = None

        self.output_anal_path = None
        
        #MORPHIOUS clustering hyperparameters
        self.nu = 0.12
        self.gamma = 0.2
        self.minN = 20
        self.min_dist = 142
        self.cvs = 5
        self.find_focal_clusters = False
        self.focal_minN = 5
        self.focal_feature = "IntDen"
        
        #features
        self.all_features = None
        self.selected_features = None
        
        #use principle component analysis
        self.use_pca = False
        self.nPCs = None #number of principle components
        
        #path for output cluster files
        self.output_cluster_path = None
        self.output_df_path = None
        
        #grid search parameters
        self.nu_start = 0.1
        self.nu_end = 0.11
        self.nu_incr = 2
        
        self.gamma_start = 0.2
        self.gamma_end = 0.2
        self.gamma_incr = 1
        
        self.minN_start = 20
        self.minN_end = 20
        self.minN_incr = 1
        
        
        self.gridsearch_output_path = None #output path for CV/train and test grid search results
        self.summ_param_output_path = None #output path for final parameter summary file
        
        self.grid_cv_file = None #grid search results for the training set
        self.grid_test_file = None #grid search results for the test set
    
    #constructors to open GUI frames
    def open_main_frame(self):
        '''
        Opens the initial program frame

        Returns
        -------
        None.

        '''
        if(self.main_frame==None):
            self.main_frame = morphious_gui.main_frame(self)
        
    def open_morphious_frame(self):
        '''
        Opens the main MORPHIOUS frame, contains all steps for running MORPHIOUS

        Returns
        -------
        None.

        '''
        if self.morphious_frame == None:
            self.morphious_frame = morphious_gui.MORPHIOUS_frame(self)
            
    def open_control_frame(self):
        '''
        opens the frame to load training data set

        Returns
        -------
        None.

        '''
        if self.train_option_frame == None:
            self.train_option_frame = morphious_gui.load_data_frame(self, train_load=True)
            
    def open_test_frame(self):
        '''
        opens the frame to load test data set

        Returns
        -------
        None.

        '''
        if self.test_option_frame == None:
            self.test_option_frame = morphious_gui.load_data_frame(self, train_load=False)
            
    def open_cluster_frame(self):
        '''
        opens the find clusters frame

        Returns
        -------
        None.

        '''
        if self.cluster_frame == None:
            self.cluster_frame = morphious_gui.cluster_frame(self)
            
    def open_feature_frame(self):
        '''
        opens the select features frame

        Returns
        -------
        None.

        '''
        if self.features_frame == None:
            self.features_frame = morphious_gui.features_frame(self)
    
    def open_focal_feature_frame(self):
        '''
        opens the select focal feature frame

        Returns
        -------
        None.

        '''
        if self.focal_feature_frame == None:
            self.focal_feature_frame = morphious_gui.focal_feature_frame(self)
            
    def open_save_frame(self):
        '''
        opens the frame for saving cluster result datasets

        Returns
        -------
        None.

        '''
        if self.save_frame == None:
            self.save_frame = morphious_gui.save_cluster_frame(self)
    def open_save_df_frame(self):
        '''

        '''
        if self.save_df_frame == None:
            self.save_df_frame = morphious_gui.save_df_frame(self)
            
    def open_grid_search_frame(self):
        '''
        opens the frame for running a grid search

        Returns
        -------
        None.

        '''
        if self.grid_search_frame == None:
            self.grid_search_frame = morphious_gui.grid_search_frame(self)

    def open_analysis_frame(self):
        '''
        opens the post cluster analysis frame

        Returns
        -------
        None.

        '''
        if self.analysis_selector_frame == None:
            self.analysis_selector_frame = morphious_gui.analysis_selector_frame(self)
    
    def open_subanalysis_frame(self, analysis_protocol, title='Immunofluorescence analysis', cell_data=False):
        """opens an analysis protocol frame - either immunofluorescence and cluster, or skeleton and cell analysis

        Args:
            analysis_protocol (str): analysis protcol, choices are "IF", or "Skeleton"
            title (str, optional): title of frame. Defaults to 'Immunofluorescence analysis'.
            cell_data (bool, optional): whether to include a frame for cell analysis. Defaults to False.
        """
        if analysis_protocol == 'IF':
            if self.IF_analysis_frame == None:
                self.IF_analysis_frame = morphious_gui.subanalysis_frame(self, analysis_protocol, title=title, cell_data=cell_data)
            else:
                morphious_gui.close_analysis_frame_warning()
        if analysis_protocol == 'Skeleton':
            if self.skel_analysis_frame == None:
                self.skel_analysis_frame = morphious_gui.subanalysis_frame(self, analysis_protocol, title=title, cell_data=cell_data)
            else:
                morphious_gui.close_analysis_frame_warning()
            
    #analysis functions
    def load_anal_data(self, protocol):
        """ load the data to be analyzed
        Args:
            protocol (str): analysis protocol

        Returns:
            pandas dataframe: dataframe of loaded data
        """
        to_return = None
        if protocol == 'IF':
            self.IF_anal_df = morphious_input.read_IF_anal_data(path=self.IF_anal_path)
            df = self.IF_anal_df
            to_return = df['file'].values

        if protocol == "Skeleton":
            if self.skel_anal_path is not None:
                self.skel_anal_df = morphious_input.read_skel_anal_data(path=self.skel_anal_path)
                to_return = self.skel_anal_df['file'].values #overwritten if both frames are present
            
            if self.cell_anal_path is not None:
                self.cell_anal_df = morphious_input.read_cell_anal_path(path=self.cell_anal_path)
                to_return = self.cell_anal_df['file'].values #overwritten if both frames are present

            #if both cell and skeleton data is loaded, find a consistent set of filenames for the grouping procedure
            if ((self.skel_anal_df is not None) and (self.cell_anal_df is not None)):
                files = np.intersect1d(self.skel_anal_df['file'].values, self.cell_anal_df['file'].values)
                unmatched_files = np.setdiff1d(self.skel_anal_df['file'].values, self.cell_anal_df['file'].values)
                if len(files) == 0:
                    print("ERROR! all skeleton and cell file names do not match")
                    morphious_gui.error_box(title="Error!", message="Error! Skeleton and cell file names do not match analysis cannot be completed, try running skeleton and cell analyses seperately")
                elif len(unmatched_files) > 0:
                    print("WARNING! some skeleton and cell file names do not match")
                    morphious_gui.warning_box(title="Warning!", message="WARNING! some skeleton and cell file names do not match\n unmatched files are removed from the analysis")
                    to_return = files
                else:
                    to_return = files
        return to_return

    def perform_skel_and_cell_analysis(self, groups_dict):
        """perform skeleton and cell analysis

        Args:
            groups_dict (dictionary): file : group dictionary to regroup analysis
        """
        if self.output_anal_path is None:
            print("Error!")
            morphious_gui.error_box(title='Error!', message='Select a location to save your analysis file to')
        else:
            print('running analysis...')
            skel_df = None
            cell_df = None
            output_str = []
            if self.skel_anal_df is not None:
                skel_df = morphious_analysis.regroup_data(self.skel_anal_df, groups_dict)
                output_str += ['skeleton']
            if self.cell_anal_df is not None:
                cell_df = morphious_analysis.regroup_data(self.cell_anal_df, groups_dict)
                output_str += ['cell']
            
            regrouped_df = morphious_analysis.skeleton_and_cell_analysis(skel_df, cell_df)
            morphious_analysis.save_file(regrouped_df, self.output_anal_path, "_".join(output_str))
            morphious_gui.complete_box(title='', message='Analysis Complete!')

    def perform_IF_analysis(self, groups_dict):
        """perform immunofluorescence analysis

        Args:
            groups_dict (dictionary): file : group dictionary to regroup analysis
        """
        if self.output_anal_path is None:
            print("Error!")
            morphious_gui.error_box(title='Error!', message='Select a location to save your analysis file to')
        else:
            print('running analysis...')
            regrouped_df = morphious_analysis.regroup_data(self.IF_anal_df, groups_dict)
            regrouped_df = morphious_analysis.IF_and_cluster_analysis(regrouped_df)
            morphious_analysis.save_file(regrouped_df, self.output_anal_path, "IF")
            morphious_gui.complete_box(title='', message='Analysis Complete!')

    #input functions
    def load_data(self, train):
        '''
        load feature data from the selected features paths.
        At least one path must be input.

        Parameters
        ----------
        train : boolean
            defines whether the loaded data should be saved as the train_df (train == True),
            or, should be saved as the test_df (train==False).

        Returns
        -------
        bool
            whether the data has been successfully loaded.

        '''
        if( not (bool(self.feature_path) or bool(self.fractal_path) or bool(self.skeleton_path) or bool(self.cell_path) or bool(self.user_data_path))):
            print('error atleast one path is needed')
            return False
        else:
            if bool(self.user_data_path):
                # print(self.user_data_path)
                try:
                    df = pd.read_csv(self.user_data_path, sep=",")
                except:
                    print("error.. not a valid .csv file")
                    return False
                if not ("file" in df.columns.values):
                    print("error.. a 'file' column is not present in the datafile")
                    return False
                
            else:
                df = morphious_input.compile_feature_df(feature_path=self.feature_path, fractal_path=self.fractal_path, 
                                   skeleton_path=self.skeleton_path, cell_count_path=self.cell_path,
                                   scale = self.scale, boxsize = self.boxsize)
            if(train):
                self.train_df = df
                if self.df_path is not None:
                    self.train_df.to_csv(self.df_path+"/train_data.csv")
            
            else:
                self.test_df = df
                if self.df_path is not None:
                    self.train_df.to_csv(self.df_path+"/test_data.csv")
            self.reset_file_paths()
            return True
                
    
    def reset_file_paths(self):
        '''
        resets all file paths to None, resets saved path data.

        Returns
        -------
        None.

        '''
        self.feature_path = None
        self.fractal_path = None
        self.skeleton_path = None
        self.cell_path = None
        self.user_data_path = None
        self.df_path = None
    
    #cluster functions
    def return_numeric_features(self):
        '''
        finds all numeric columns present in the training dataframe.

        Returns
        -------
        numpy array
            features of type numeric present in the training dataframe.

        '''
        x = morphious_cluster.get_numeric_cols(self.train_df)
        return x.columns.values
        
    def find_clusters(self, cv=False):
        '''
        finds clusters in either the training dataset (cv == True), or in the test dataset (cv == False)
        MORPHIOUS parameters are retrieved from the saved parameters in the controller object
    
        Parameters
        ----------
        cv : boolean, optional
            defines whether to find clusters in the training set via cross-validation, 
            or, find clusters in the test dataset. The default is False.

        Returns
        -------
        None.

        '''
        
        print(f"MORPHIOUS PARAMETERS -- Nu: {self.nu}, Gamma: {self.gamma}, minimum cluster size: {self.minN}, minimum distance: {self.min_dist}")
        
        #run cross-validation on the training set
        if cv:
            print(f"cross-validation, number of CVs: {self.cvs}")
            
            #find clusters in the train set via cross validation
            train = morphious_cluster.iter_all_one_model(self.train_df, None, features=self.selected_features,extra_scalers=["IntDen"],
                           cross_validate_one_group=True, CVs = self.cvs,
                       scale='standard',
                           gamma=self.gamma, nu=self.nu, kernel='rbf', minN=self.minN, eps=self.min_dist,
                           focal_cluster=False,focal_minN=5,focal_feature="IntDen",
                           pca=self.use_pca,n_comps=self.nPCs,return_pca_model=False,
                          relabel_clusters=True, combine=False, label_unclustered=True, unclustered_reference='proximal_clusters',
                          groupby=['file'])
            
            self.cv_clusters=train
        
        else:
            #find clusters in the test set
            combine=False
            unclustered_reference='proximal_clusters' #defines unclusters as not "proximal_clusters"
            
            if self.find_focal_clusters:
                combine=True #combined_clusters = focal_clusters + proximal_clusters
                unclustered_reference="combined_clusters" #defines unclustered as not "combined_clusters"
            
            # find clusters in the test data set
            # note, clusters are not searched for in the train set, it is only used for training purposes
            train, test = morphious_cluster.iter_all_one_model(self.train_df, self.test_df, features=self.selected_features,extra_scalers=["IntDen"],
                           cross_validate_one_group=False, CVs = self.cvs,
                       scale='standard',
                           gamma=self.gamma, nu=self.nu, kernel='rbf', minN=self.minN, eps=self.min_dist,
                           focal_cluster=self.find_focal_clusters,focal_minN=self.focal_minN,focal_feature="IntDen",
                           pca=self.use_pca,n_comps=self.nPCs,return_pca_model=False,
                          relabel_clusters=True, combine=combine, label_unclustered=True, unclustered_reference=unclustered_reference,
                          groupby=['file'])
            
            self.test_clusters = test
        morphious_gui.complete_box(title="Success!", message="Find cluster procedure completed!")
    
    #gridsearch functions
    def grid_search(self, cv=False):
        '''
        run a grid search on either the training dataset via cross-validation (cv == True),
        or, on the test set (cv == False). Parameters are retrieved from the controller's saved attributed

        Parameters
        ----------
        cv : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None.

        '''
        nu_range=[float(self.nu_start),float(self.nu_end),int(self.nu_incr)]
        gamma_range=[float(self.gamma_start),float(self.gamma_end), int(self.gamma_incr)] 
        minN_range=[float(self.minN_start),float(self.minN_end),int(self.minN_incr)]
        
        #run grid search on the traing set via cross validation
        if cv:
            test = None #test input is ignored
            train = self.train_df
            
            grid = morphious_gridsearch.grid_search_one_model(train, test, features=self.selected_features,
                          kernel='rbf', gamma_range=gamma_range,nu_range=nu_range, minN_range=minN_range,
                          eps = self.min_dist, pca=self.use_pca, nPCs = self.nPCs, scale='standard',
                          cross_validate_one_group=True, CVs=self.cvs,
                          focal_cluster=False,focal_minN=5,focal_feature="IntDen",
                          summarize_clusters=True, groupby = ['file'], summary_keys=['gamma','nu','minN'], 
                          summary_clusters=['proximal_clusters'])
            
        
            
        else:
            train = self.train_df
            test = self.test_df
            
            #run a grid search training on the train data and testing on the test data
            grid = morphious_gridsearch.grid_search_one_model(train, test, features=self.selected_features,
                          kernel='rbf', gamma_range=gamma_range,nu_range=nu_range, minN_range=minN_range,
                          eps = self.min_dist, pca=self.use_pca, nPCs = self.nPCs, scale='standard',
                          cross_validate_one_group=False, CVs=self.cvs,
                          focal_cluster=False,focal_minN=5,focal_feature="IntDen",
                          summarize_clusters=True, groupby = ['file'], summary_keys=['gamma','nu','minN'], 
                          summary_clusters=['proximal_clusters'])
            
            
        morphious_gridsearch.save_grids(grid, self.gridsearch_output_path, cv=cv, nCVs=self.cvs)
        morphious_gui.complete_box(title="Complete!", message="Grid Search Complete!")
        
    def find_optimal_params(self):
        '''
        reads the train set and test set grid search files and identifies the set of parameters
        which yield no clusters in the training set, and maximize clustering in the test set

        Returns
        -------
        None.

        '''
        
        #read in train and test set data frames
        cv_df = pd.read_csv(self.grid_cv_file)
        test_df = pd.read_csv(self.grid_test_file)
        
        #resummarize to combine cluster results across images
        cv_df = morphious_gridsearch.resummarize_cluster_grids(cv_df, keys = ['gamma','nu','minN'])
        test_df = morphious_gridsearch.resummarize_cluster_grids(test_df, keys = ['gamma','nu','minN'])
        
        #compare training and test dataframes and find the best parameters
        x = morphious_gridsearch.find_best_parameters(cv_df, test_df, cluster_metric='proximal_clusters_perc_cluster')
        
        #get the train and test grid search file names
        cv_fname = self.grid_cv_file.split("/")[-1][:-4]
        test_fname = self.grid_test_file.split("/")[-1][:-4]
        
        output_file = f"optimal_params_{cv_fname}_V_{test_fname}.csv"
        x.to_csv(self.summ_param_output_path + "/" + output_file, header=True)
        print(x)
        
            
    def check_pca_variance(self, nPCs, features):
        '''
        Measures the variance associated with principle components

        Parameters
        ----------
        nPCs : int
            number of principle components to calculate.
        features : list-like
            features to calculate the principle components for.

        Returns
        -------
        float
            variance accounted for by the number of PCs selected.

        '''
        if self.train_df is not None:
            train, test = morphious_cluster.standard_scale(self.train_df.copy(),None,features=features,dropna=True,newcols=True, scale='standard')
            pca_model = morphious_cluster.pca_transform_features(train, None, features, nPCs, only_model=True)
            return pca_model.explained_variance_ratio_.sum()

        else:
            print("ERROR!")
        
    def save_clusters(self, selection):
        '''
        writes clusters to coordinate files

        Parameters
        ----------
        selection : int
            selects the data frame to save.

        Returns
        -------
        None.

        '''
        
        clusters = ["proximal_clusters"]
        unclustered_reference = "proximal_clusters"
        
        if selection == 1:
            df = self.cv_clusters
        elif selection == 2:
            df = self.test_clusters
            if self.find_focal_clusters:
                clusters.append("focal_clusters")
                clusters.append("combined_clusters")
                unclustered_reference = 'combined_clusters'
        else:
            morphious_gui.warning_box(title="Warning!", message="Please select a cluster data frame")
            return None
        
        morphious_write_clusters.write_all_cluster_files(df, clusters=clusters,path=self.output_cluster_path,
                           write_unclustered=True, unclustered_reference = unclustered_reference, unclustered_output="unclustered",
                           groupby = ["file"])

    def save_df(self, selection):
        '''
        writes train or test df to file

        Parameters
        ----------
        selection : int
            selects the dataframe to save.

        Returns
        -------
        None.

        '''
        if selection == 1:
            df = self.cv_clusters
            f = "processed_train_df.csv"
        elif selection == 2:
            df = self.test_clusters
            f = "processed_test_df.csv"
        else:
            morphious_gui.warning_box(title="Warning!", message="Please select a dataset")
            return None
        
        df.to_csv(os.path.join(self.output_df_path, f))


    
        #controller functions
    def truncate_label_string(self, labelstr, max_length=25):
        '''
        trunates a string and precedes it by "..." for input into a label

        Parameters
        ----------
        labelstr : String
            string to be truncated.
        max_length : int, optional
            length of the resultant string. The default is 25.

        Returns
        -------
        re : String
            a string of length 25 preceded by "...".

        '''
        re = labelstr
        if labelstr is not None:
            if(len(labelstr)>max_length):
                trunc = "..."+labelstr[-1*max_length+3:-1]+labelstr[-1]
                print(len(trunc))
                re = trunc
        return re
        
        
