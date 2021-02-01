# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 14:43:36 2020

@author: joey_
"""
from morphious_input import *
from morphious_gui import *
from morphious_cluster import *
from morphious_write_clusters import *
from morphious_gridsearch import *

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
        self.console_frame = None
        self.grid_search_frame = None
        self.save_frame = None
        
        #paths to feature files
        self.feature_path = None
        self.fractal_path = None
        self.skeleton_path = None
        self.cell_path = None
        self.df_path = None
        self.boxsize = None #boxsize used for extracting features
        self.scale = None #scale of the images
        
        #MORPHIOUS clistering hyperparameters
        self.nu = 0.12
        self.gamma = 0.2
        self.minN = 20
        self.min_dist = 128
        self.cvs = 5
        self.find_focal_clusters = False
        self.focal_minN = 5
        
        #features
        self.all_features = None
        self.selected_features = None
        
        #use principle component analysis
        self.use_pca = False
        self.nPCs = None #number of principle components
        
        #path for output cluster files
        self.output_cluster_path = None
        
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
            self.main_frame = main_frame(self)
        
    def open_morphious_frame(self):
        '''
        Opens the main MORPHIOUS frame, contains all steps for running MORPHIOUS

        Returns
        -------
        None.

        '''
        if self.morphious_frame == None:
            self.morphious_frame = MORPHIOUS_frame(self)
            
    def open_control_frame(self):
        '''
        opens the frame to load training data set

        Returns
        -------
        None.

        '''
        if self.train_option_frame == None:
            self.train_option_frame = load_data_frame(self, train_load=True)
            
    def open_test_frame(self):
        '''
        opens the frame to load test data set

        Returns
        -------
        None.

        '''
        if self.test_option_frame == None:
            self.test_option_frame = load_data_frame(self, train_load=False)
            
    def open_cluster_frame(self):
        '''
        opens the find clusters frame

        Returns
        -------
        None.

        '''
        if self.cluster_frame == None:
            self.cluster_frame = cluster_frame(self)
            
    def open_feature_frame(self):
        '''
        opens the select features frame

        Returns
        -------
        None.

        '''
        if self.features_frame == None:
            self.features_frame = features_frame(self)
            
    def open_save_frame(self):
        '''
        opens the frame for saving cluster result datasets

        Returns
        -------
        None.

        '''
        if self.save_frame == None:
            self.save_frame = save_cluster_frame(self)
            
    def open_grid_search_frame(self):
        '''
        opens the frame for running a grid search

        Returns
        -------
        None.

        '''
        if self.grid_search_frame == None:
            self.grid_search_frame = grid_search_frame(self)
            
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
        if( not (bool(self.feature_path) or bool(self.fractal_path) or bool(self.skeleton_path) or bool(self.cell_path))):
            print('error atleast one path is needed')
            return False
        else:
            df = compile_feature_df(feature_path=self.feature_path, fractal_path=self.fractal_path, 
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
        self.df_path = None
        
    def return_numeric_features(self):
        '''
        finds all numeric columns present in the training dataframe.

        Returns
        -------
        numpy array
            features of type numeric present in the training dataframe.

        '''
        x = get_numeric_cols(self.train_df)
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
            train = iter_all_one_model(self.train_df, None, features=self.selected_features,extra_scalers=["IntDen"],
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
            train, test = iter_all_one_model(self.train_df, self.test_df, features=self.selected_features,extra_scalers=["IntDen"],
                           cross_validate_one_group=False, CVs = self.cvs,
                       scale='standard',
                           gamma=self.gamma, nu=self.nu, kernel='rbf', minN=self.minN, eps=self.min_dist,
                           focal_cluster=self.find_focal_clusters,focal_minN=self.focal_minN,focal_feature="IntDen",
                           pca=self.use_pca,n_comps=self.nPCs,return_pca_model=False,
                          relabel_clusters=True, combine=combine, label_unclustered=True, unclustered_reference=unclustered_reference,
                          groupby=['file'])
            
            self.test_clusters = test
            
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
            
            grid = grid_search_one_model(train, test, features=self.selected_features,
                          kernel='rbf', gamma_range=gamma_range,nu_range=nu_range, minN_range=minN_range,
                          eps = 128, pca=self.use_pca, nPCs = self.nPCs, scale='standard',
                          cross_validate_one_group=True, CVs=self.cvs,
                          focal_cluster=False,focal_minN=5,focal_feature="IntDen",
                          summarize_clusters=True, groupby = ['file'], summary_keys=['gamma','nu','minN'], 
                          summary_clusters=['proximal_clusters'])
            
        
            
        else:
            train = self.train_df
            test = self.test_df
            
            #run a grid search training on the train data and testing on the test data
            grid = grid_search_one_model(train, test, features=self.selected_features,
                          kernel='rbf', gamma_range=gamma_range,nu_range=nu_range, minN_range=minN_range,
                          eps = 128, pca=self.use_pca, nPCs = self.nPCs, scale='standard',
                          cross_validate_one_group=False, CVs=self.cvs,
                          focal_cluster=False,focal_minN=5,focal_feature="IntDen",
                          summarize_clusters=True, groupby = ['file'], summary_keys=['gamma','nu','minN'], 
                          summary_clusters=['proximal_clusters'])
            
            
        save_grids(grid, self.gridsearch_output_path, cv=cv, nCVs=self.cvs)
        
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
        cv_df = resummarize_cluster_grids(cv_df, keys = ['gamma','nu','minN'])
        test_df = resummarize_cluster_grids(test_df, keys = ['gamma','nu','minN'])
        
        #compare training and test dataframes and find the best parameters
        x = find_best_parameters(cv_df, test_df, cluster_metric='proximal_clusters_perc_cluster')
        
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
            train, test = standard_scale(self.train_df.copy(),None,features=features,dropna=True,newcols=True, scale='standard')
            pca_model = pca_transform_features(train, None, features, nPCs, only_model=True)
            return pca_model.explained_variance_ratio_.sum()
            #print(pca_model.explained_variance_ratio_, 'explains: ',pca_model.explained_variance_ratio_.sum())

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
            print("Please select a cluster data frame")
            return None
        
        write_all_cluster_files(df,clusters=clusters,
                            path=self.output_cluster_path,
                           write_unclustered=True, unclustered_reference = unclustered_reference, unclustered_output="unclustered",
                           groupby = ["file"])
        
        