# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 23:09:13 2020

@author: joey_
"""

from tkinter import *
from tkinter import filedialog
import numpy as np


             
# main window of program, launches macro writing and MORPHIOUS frames   
class main_frame(object):
    
    def __init__(self, controller):
        '''
        

        Parameters
        ----------
        controller : controller object
            initializes the main frame window.

        Returns
        -------
        None.

        '''
        
        self.root=Tk()
        self.root.title("MORPHIOUS")
        #self.root.geometry("400x400")
        
        self.morphious_frame = None
        
        self.extract_data_frame = LabelFrame(self.root, text="generate data", padx=2, pady=2)
        self.extract_data_frame.grid(row=0, column=0)
        #self.write_macro_button = Button(self.extract_data_frame, text="write imageJ macros" )
        #self.write_macro_button.grid(row=0,column=0)
        
        self.read_data_frame = LabelFrame(self.root, text="run MORPHIOUS", padx=2, pady=2)
        self.read_data_frame.grid(row=1, column=0)
        self.read_data_button = Button(self.read_data_frame, text="open MORPHIOUS", command= lambda: controller.open_morphious_frame())
        self.read_data_button.grid(row=0,column=0, padx=50)
        
        mainloop()
        
        
        
# main MORPHIOUS frame, used to access data loading and clustering frames       
class MORPHIOUS_frame(object):
    
    def __init__(self, controller):
        '''
        initializes the MORPHIOUS_frame object, 
        this frame provides buttons to load feature data, find clusters, save cluster data, and conduct grid searches

        Parameters
        ----------
        controller : controller object
            controller object to navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        
        self.window = Toplevel()
        self.window.lift()
        
        self.window.title('MORPHIOUS options')
        self.window.protocol('WM_DELETE_WINDOW', lambda : self.on_tl_close(controller))
        
        #input data frame
        self.data_input_frame = LabelFrame(self.window, text="input data", padx=2, pady=2)
        self.data_input_frame.grid(row=0,column=0)
        
        self.b1 = Button(self.data_input_frame, text='load control data', command= lambda: controller.open_control_frame()).grid(row=1, column=0)
        self.b2 = Button(self.data_input_frame, text='load test data', command= lambda: controller.open_test_frame()).grid(row=2, column=0)
        #self.check_button = Button(self.data_input_frame, text='check_value', command = lambda: controller.print_var_data()).grid(row=3, column=1)
    
        #cluster frame
        self.cluster_frame = LabelFrame(self.window, text="Find Clusters", padx=2, pady=2)
        self.cluster_frame.grid(row=3, column=0, padx=10, pady=10)
        self.b3 = Button(self.cluster_frame, text="Find Clusters", command=lambda : controller.open_cluster_frame()).grid(row=4,column=0)
        self.b4 = Button(self.cluster_frame, text="Save Clusters", command=lambda : controller.open_save_frame()).grid(row=5,column=0)
        self.b5 = Button(self.cluster_frame, text="Grid Search Parameters", command=lambda : controller.open_grid_search_frame()).grid(row=6,column=0)
    
    
    def on_tl_close(self, controller):
        '''
        closes frame

        Parameters
        ----------
        controller : controller object
            controller object to navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.window.destroy()
        controller.morphious_frame = None
        
        
    
# frame for loading training and test data into the program     
class load_data_frame(object):
    def __init__(self, controller, train_load=True):
        '''
        initializes the feature data loading frame

        Parameters
        ----------
        controller : controller object
            controller object to navigate between GUI and morphious back-end.
        train_load : boolean, optional
            defines whether the training or test set is being loaded. The default is True.

        Returns
        -------
        None.

        '''
        
        self.window = Toplevel()
        self.window.lift()
        
        self.window.title('load data')
        self.window.protocol('WM_DELETE_WINDOW', lambda : self.on_tl_close(controller, train_load))
        
        self.feature_frame = LabelFrame(self.window, text='load intensity features')
        self.feature_dir_button = Button(self.feature_frame, text='select intensity features directory', command= lambda:self.set_feature_path(controller))
        self.feature_dir_label = Label(self.feature_frame, text=controller.feature_path, relief=RIDGE, width=25)
        
        self.fractal_frame = LabelFrame(self.window, text='load fractal features')
        self.fractal_dir_button = Button(self.fractal_frame, text='select fractal features directory', command= lambda:self.set_fractal_path(controller))
        self.fractal_dir_label = Label(self.fractal_frame, text=controller.fractal_path, relief=RIDGE, width=25)
        
        self.skeleton_frame = LabelFrame(self.window, text='load skeleton features')
        self.skeleton_dir_button = Button(self.skeleton_frame, text='select skeleton features directory', command= lambda:self.set_skeleton_path(controller))
        self.skeleton_dir_label = Label(self.skeleton_frame, text=controller.skeleton_path, relief=RIDGE, width=25)
        
        self.cell_frame = LabelFrame(self.window, text='load cell features')
        self.cell_dir_button = Button(self.cell_frame, text='select cell features directory', command= lambda:self.set_cell_path(controller))
        self.cell_dir_label = Label(self.cell_frame, text=controller.cell_path, relief=RIDGE, width=25)
        
        self.boxsize_label = Label(self.window, text="Enter the box size").grid(row=2, column=0)
        self.boxsize_entry = Entry(self.window, width=10)
        
        self.save_df_button = Button(self.window, text="Enter path to save data (optional)", command = lambda : self.set_output_df_dir(controller))
        self.save_df_button.grid(row=4, column=0)
        
        self.output_df_dir_label = Label(self.window, text=controller.truncate_label_string(controller.df_path), relief=RIDGE, width=25)
        self.output_df_dir_label.grid(row=4, column=1)
        
        if controller.boxsize is None:
            insert = "150"
        else:
            insert = str(controller.boxsize)
        self.boxsize_entry.insert(END, insert)
        self.boxsize_entry.grid(row=2, column=1)
        
        self.scale_label = Label(self.window, text="Enter the image scale (um/pixel)").grid(row=3, column=0)
        self.scale_entry = Entry(self.window, width=10)
        if controller.scale is None:
            insert = "1.5"
        else:
            insert = str(controller.scale)
        self.scale_entry.insert(END, insert)
        self.scale_entry.grid(row=3, column=1)
        
        self.load_button = Button(self.window, text = 'load data', padx = 50, pady = 10,
                                  command= lambda: self.load_data(controller, train_load))
        
        
        index=0
        #adds all buttos and labels to the grid
        for frame, button, label in zip([self.feature_frame, self.fractal_frame, self.skeleton_frame, self.cell_frame],
                                        [self.feature_dir_button, self.fractal_dir_button, self.skeleton_dir_button, self.cell_dir_button],
                                        [self.feature_dir_label, self.fractal_dir_label, self.skeleton_dir_label, self.cell_dir_label]):
            
            frame.grid(row=0, column=index)
            button.grid(row=1, column=index)
            label.grid(row=2, column=index)
            index += 1



        self.load_button.grid(row=5, column=0, columnspan=4, padx=50)
        self.feature_dir_button.grid(row=0, column=0)
        self.feature_dir_label.grid(row=1, column=0)
        
        
    def set_feature_path(self, controller):
        '''
        saves a feature path to load data with

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        controller.feature_path = filedialog.askdirectory(initialdir="")
        self.set_feature_label(controller)
        self.window.lift()
        
    def set_feature_label(self, controller):
        '''
        updates the feature label with the saved feature path

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.feature_dir_label.grid_remove()
        self.feature_dir_label = Label(self.feature_frame, text=controller.truncate_label_string(controller.feature_path), relief=RIDGE, width=25)
        self.feature_dir_label.grid(row=2, column=0)
        
    def set_fractal_path(self, controller):
        '''
       saves the path for loading fractal data

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        controller.fractal_path = filedialog.askdirectory(initialdir="")
        self.set_fractal_label(controller)
        self.window.lift()
        
    def set_fractal_label(self, controller):
        '''
        updates the fractal path label with the saved fractal data path

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.fractal_dir_label.grid_remove()
        self.fractal_dir_label = Label(self.fractal_frame, text=controller.truncate_label_string(controller.fractal_path), relief=RIDGE, width=25)
        self.fractal_dir_label.grid(row=2, column=1)
        
    def set_skeleton_path(self, controller):
        '''
       saves the path for loading skeleton feature data

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        controller.skeleton_path = filedialog.askdirectory(initialdir="")
        self.set_skeleton_label(controller)
        self.window.lift()
        
    def set_skeleton_label(self, controller):
        '''
        updates the skeleton path label with the saved skeleton data path

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.skeleton_dir_label.grid_remove()
        self.skeleton_dir_label = Label(self.skeleton_frame, text=controller.truncate_label_string(controller.skeleton_path), relief=RIDGE, width=25)
        self.skeleton_dir_label.grid(row=2, column=2)
        
    def set_cell_path(self, controller):
        '''
       saves the path for loading cell feature data

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        controller.cell_path = filedialog.askdirectory(initialdir="")
        self.set_cell_label(controller)
        self.window.lift()
        
    def set_cell_label(self, controller):
        '''
        updates the cell path label with the saved cell data path

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.cell_dir_label.grid_remove()
        self.cell_dir_label = Label(self.cell_frame, text=controller.truncate_label_string(controller.cell_path), relief=RIDGE, width=25)
        self.cell_dir_label.grid(row=2, column=3)
        
    def set_output_df_dir(self, controller):
        '''
        sets an output directory to save loaded features into a dataset

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        controller.df_path = filedialog.askdirectory(initialdir="")
        self.output_df_dir_label.grid_remove()
        self.output_df_dir_label = Label(self.window, text=controller.truncate_label_string(controller.df_path), relief=RIDGE, width=25)
        self.output_df_dir_label.grid(row=4, column=1)
        self.window.lift()
    
    def on_tl_close(self, controller, train_load):
        '''
        closes data load frame

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        train_load : boolean
            defines where its the train or test dataframe which is loaded.

        Returns
        -------
        None.

        '''
        self.window.destroy()
        if(train_load):
            controller.train_option_frame = None
        else:
            controller.test_option_frame = None
        
    def load_data(self, controller, train_load):
        '''
        loads the data based on the stores feature path information

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        train_load : boolean
            defines where its the train or test dataframe which is loaded.

        Returns
        -------
        None.

        '''
        controller.boxsize = float(self.boxsize_entry.get())
        controller.scale = float(self.scale_entry.get())
        loaded = controller.load_data(train_load)
        if loaded:
            self.on_tl_close(controller, train_load)
        else:
            print("Error!")
    
                
#frame for MORPHIOUS cluster functions     
class cluster_frame(object):
    def __init__(self, controller):
        '''
        frame to define cluster parameters and to generate clusters of activated cells

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        
        self.window = Toplevel()
        self.window.lift()
        
        self.window.title('Find Cluster ROIs')
        self.window.protocol('WM_DELETE_WINDOW', lambda : self.on_tl_close(controller))
        
        self.param_frame = LabelFrame(self.window, text='MORPHIOUS parameters')
        self.param_frame.grid(row=0, column=0)
        
        self.nu_label = Label(self.param_frame, text="Enter Nu value").grid(row=0, column=0)
        self.nu_input = Entry(self.param_frame, width=10)
        self.nu_input.grid(row=0, column=1)
        self.nu_input.insert(END, controller.nu)
        
        self.gamma_label = Label(self.param_frame, text="Enter gamma value").grid(row=1, column=0)
        self.gamma_input = Entry(self.param_frame, width=10)
        self.gamma_input.grid(row=1, column=1)
        self.gamma_input.insert(END, controller.gamma)
        
        self.minN_label = Label(self.param_frame, text="Enter minimum cluster size").grid(row=2, column=0)
        self.minN_input = Entry(self.param_frame, width=10)
        self.minN_input.grid(row=2, column=1)
        self.minN_input.insert(END, controller.minN)
        
        self.min_dist_label = Label(self.param_frame, text="Enter minimum distance").grid(row=3, column=0)
        self.min_dist_input = Entry(self.param_frame, width=10)
        self.min_dist_input.grid(row=3, column=1)
        self.min_dist_input.insert(END, controller.min_dist)
        
        self.focal_cluster_bin = BooleanVar()
        self.focal_cluster_check = Checkbutton(self.param_frame, text="find focal clusters", 
                                               variable = self.focal_cluster_bin, 
                                               command=lambda : self.select_focal_clusters(controller))
        self.focal_cluster_check.deselect()
        self.focal_cluster_check.grid(row=4, column=0, columnspan=2)

        
        self.minN_focal_label = Label(self.param_frame, text="Enter minimum focal cluster size").grid(row=5, column=0)
        self.minN_focal_input = Entry(self.param_frame, width=10, state=DISABLED)
        self.minN_focal_input.grid(row=5, column=1)
        self.minN_focal_input.insert(END, controller.focal_minN)
        
        
        #self.calc_min_dist = Button(self.window, text="calculate default distance").grid(row=, column=0)
        
        self.selection = IntVar()
        self.selection.set("1")
        
        self.cv_frame = LabelFrame(self.window, text = "Cross Validate Training Set")
        self.cv_frame.grid(row=0, column=1)
        self.train_set_loaded = self.check_data_set_load(controller, train=True) # returns a label and sets radiobutton
        self.train_set_loaded.grid(row=0, column=1)
        
        self.cv_input = Entry(self.cv_frame, width=5)
        self.cv_input_label = Label(self.cv_frame, text="Enter # of cross validations").grid(row=2,column=1)
        self.cv_input.grid(row=2, column=2,padx=10)
        self.cv_input.insert(END, controller.cvs)
        
        self.cluster_frame = LabelFrame(self.window, text = "Find Clusters In Test Set")
        self.cluster_frame.grid(row=0, column=3)
        self.test_set_loaded = self.check_data_set_load(controller, train=False) # returns a label and sets radiobutton
        self.test_set_loaded.grid(row=0, column=3)
        
        #buttons
        self.features_button = Button(self.param_frame, text="Select Features", command=lambda : controller.open_feature_frame())
        self.features_button.grid(row=6, column=0, columnspan=2)
        #self.feature_loaded_label = Label(self.param_frame,text="no features selected")
        #self.feature_loaded_label.grid(row=4, column=1)
        self.save_parameters = Button(self.window, text="Run!", command=lambda: self.find_clusters(controller), padx=25, pady=10).grid(row=5, column=0, columnspan=4)
        
        
    def find_clusters(self, controller):
        '''
        saves inputed parameter data in the controller, and finds clusters of activated cells

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        
        controller.nu = float(self.nu_input.get())
        controller.gamma = float(self.gamma_input.get())
        controller.minN = int(self.minN_input.get())
        controller.min_dist = float(self.min_dist_input.get())
        controller.find_focal_clusters = self.focal_cluster_bin.get()
        
        if controller.find_focal_clusters:
            controller.focal_minN = int(self.minN_focal_input.get())
            
        if(self.selection.get()==1):
            controller.cvs = int(self.cv_input.get())
            controller.find_clusters(cv=True)
        elif(self.selection.get()==2):
            controller.find_clusters(cv=False)
                
            
    def check_data_set_load(self,controller,train=True):
        '''
        checks whether the training and set data sets are loaded, and if not, prevents the user from using that dataset

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        train : boolean, optional
            specifies which dataset to check is loaded. The default is True.

        Returns
        -------
        x : Label
            returns a label on whether the dataset is loaded.

        '''
        if train:
            loaded = False
            state = DISABLED
            if controller.train_df is not None:
                loaded = True
                state = NORMAL
            x = Label(self.cv_frame, text=f"train data loaded: {loaded}")
            
            Radiobutton(self.cv_frame, text="perform cross validation", variable=self.selection, value=1, state=state).grid(row=1,column=1)
        else:
            loaded = False
            state = DISABLED
            if controller.test_df is not None:
                loaded = True
                state = NORMAL
            x = Label(self.cluster_frame, text=f"test data loaded: {loaded}")
            Radiobutton(self.cluster_frame, text="use test set", variable=self.selection, value=2, state=state).grid(row=1,column=3)
        return x
    
    def select_focal_clusters(self, controller):
        '''
        checks whether focal clusters were selected, and generates an entry label to select a minimum focal cluster size

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.minN_focal_input.grid_remove()
        self.minN_focal_input = Entry(self.param_frame, width=10, state=NORMAL)
        self.minN_focal_input.grid(row=5, column=1)
        self.minN_focal_input.insert(END, controller.focal_minN)
    
    def on_tl_close(self, controller):
        '''
        closes frame

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.window.destroy()
        controller.cluster_frame = None


class features_frame(object):
    def __init__(self, controller):
        '''
        initializes the feature selection frame

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        
        self.window = Toplevel()
        self.window.lift()
        self.window.title('Select Features')
        self.window.protocol('WM_DELETE_WINDOW', lambda : self.on_tl_close(controller))
        
        self.feats_frame = LabelFrame(self.window, text='Select Features For Identifying Activated Cells')
        self.feats_frame.grid(row=0, column=0)
        
        self.checkbox_listeners = []
        self.checkbuttons = []
        self.checkbuttons, self.checkbox_listeners, row_index = self.generate_checkboxes(controller, self.feats_frame)
        
        self.pca_frame = LabelFrame(self.window, text='Principal Component Analysis Transform Features')
        self.pca_frame.grid(row=row_index + 1, column=0)
        
        self.use_pca_var = IntVar()
        self.use_pca_checkbox = Checkbutton(self.pca_frame, text='PCA transform features', variable = self.use_pca_var)
        self.use_pca_checkbox.grid(row=row_index+1, column=0)
        
        self.nPCs_label = Label(self.pca_frame, text="number of Principle Components")
        self.nPCs_label.grid(row=row_index+2, column=0)
        self.nPCs = Entry(self.pca_frame, width=10)
        
        self.nPCs.grid(row=row_index+2, column=1)
        self.check_NPC_variance = Button(self.pca_frame, text="check PC variance", command = lambda: self.check_pca_variance(controller, row_index+3))
        self.check_NPC_variance.grid(row=row_index+3, column=0)
        self.pca_variance_label = Label(self.pca_frame,text="{:0.5f}".format(0))
        self.pca_variance_label.grid(row=row_index+3, column=1)
        
        
        self.load_button = Button(self.window, text="Load Features", command=lambda : self.select_features(controller))
        self.load_button.grid(row=row_index+4, column=0)
        
        self.set_check_button_setting(controller)
        
        #self.b1 = Button(self.window, text="Check values", command=lambda: self.print_var()).grid(row=1, column=0)
    
    def generate_checkboxes(self, controller, frame, next_row = 10):
        '''
        generates checkbuttons for each feature in the training dataset

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        frame : tkinter frame object
            frame to load checkboxes into.
        next_row : int, optional
            number of feature checkboxes before switching to the next row. The default is 10.

        Returns
        -------
        checkbuttons : list of tkinter checkbuttons
            DESCRIPTION.
        listeners : list
            list of intvar checkbutton variables.
        row : int
            current row that checkbuttons are loaded onto.

        '''
        checkbuttons = []
        listeners = []
        load_button = None
        row=0
        col=0
        if controller.train_df is not None:
            controller.all_features = controller.return_numeric_features()
            for feat in controller.all_features:
                v = IntVar()
                c = Checkbutton(frame, text=feat, variable = v)
                c.deselect()
                c.grid(row=row, column=col)
                checkbuttons.append(c)
                listeners.append(v)
                if(col < 10):
                    col += 1
                else:
                    col = 0
                    row += 1
        else:
            print('no train df')
            
        return checkbuttons, listeners, row
    
    def set_check_button_setting(self, controller):
        '''
        retrieves the feature names of selected features, and pre-checks them

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        index = 0
        if controller.selected_features is not None:
            for button in self.checkbuttons:
                txt = button.cget("text")
                for f in controller.selected_features:
                    if f == txt:
                        self.checkbuttons[index] = self.checkbuttons[index].select()
                index += 1
    
    def select_features(self, controller):
        '''
        saves selected features and PCA transformation settings to the controller

        Parameters
        ----------
         controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        selected_features = self.view_selected_features(controller)
        controller.selected_features = selected_features
        print(controller.selected_features)
        
        pca_bool = bool(self.use_pca_var.get())
        controller.use_pca = pca_bool
        if pca_bool:
            nPCs = int(self.nPCs.get())
            controller.nPCs = nPCs
            
        self.on_tl_close(controller)
        
    def view_selected_features(self, controller):
        '''
        converts check boxes to feature names

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        selected_features : list-like
            feature names of selected features.

        '''
        feature_indexes = []
        for l in self.checkbox_listeners:
            feature_indexes.append(l.get())
        feature_indexes = np.array(feature_indexes)
        selected_ind = np.where(feature_indexes == 1)[0]
        selected_features = []
        for i in selected_ind:
            feat = controller.all_features[i]
            selected_features.append(feat)
        return selected_features
    
    def check_pca_variance(self, controller, row):
        '''
        checkes the cummulative variance of selected principle components and generates a label of the results

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        row : int
            row to place pca variance label.

        Returns
        -------
        None.

        '''
        nPCs = int(self.nPCs.get())
        features = self.view_selected_features(controller)
        variance = float(controller.check_pca_variance(nPCs, features))
        self.pca_variance_label.grid_remove()
        self.pca_variance_label = Label(self.pca_frame,text="{:0.5f}".format(variance))
        self.pca_variance_label.grid(row=row, column=1)

    def on_tl_close(self, controller):
        '''
        closes frame

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.window.destroy()
        controller.features_frame = None
        
class save_cluster_frame(object):
    def __init__(self, controller):
        '''
        opens frame to define where cluster files should be save

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.window = Toplevel()
        self.window.lift()
        
        self.window.title('save clusters')
        self.window.protocol('WM_DELETE_WINDOW', lambda : self.on_tl_close(controller))
        
        self.radio_select = IntVar()
        self.cv_radio, self.test_radio = self.generate_radio_buttons(controller, self.radio_select)
        
        self.save_clusters_button = Button(self.window, text='Save Clusters', command = lambda : self.write_cluster_coords(controller))
        self.select_dir_button = Button(self.window, text='Select Path', command = lambda : self.select_path(controller))
        self.select_dir_button.grid(row=1, column=0)
        self.selected_dir_label = Label(self.window, text=controller.output_cluster_path, relief=RIDGE, width=30)
        self.selected_dir_label.grid(row=1, column=1, columnspan=2)
        
        self.save_clusters_button.grid(row=2, column=0, columnspan=3)
        
        
    def select_path(self, controller):
        '''
        select a path to save the clusters to

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        controller.output_cluster_path = filedialog.askdirectory(initialdir="")
        self.set_dir_label(controller)
        self.window.lift()
        
    def set_dir_label(self, controller):
        '''
        sets the selected path as a label

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.selected_dir_label.grid_remove()
        self.selected_dir_label = Label(self.window, text=controller.truncate_label_string(controller.output_cluster_path, max_length=3), relief=RIDGE, width=30)
        self.selected_dir_label.grid(row=1, column=1, columnspan=2)
        
    def generate_radio_buttons(self, controller, var):
        '''
        generates radio buttons to choose which dataframe to write clusters for

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        var : Tkinter variable object
            listener to store the state of the radiobutton in.

        Returns
        -------
        radio_buttons : TYPE
            DESCRIPTION.

        '''
        radio_buttons = []
        
        for df, txt, val in zip([controller.cv_clusters, controller.test_clusters],
                      ["cross validation results",  "test dataset results"],
                      [1,2]):
            
            if df is not None:
                state = NORMAL
            else:
                state = DISABLED
            r = Radiobutton(self.window, text=txt, variable=var, value=val, state=state)
            r.grid(row=0, column=val-1)
            radio_buttons.append(r)
            
        return radio_buttons
    
    def write_cluster_coords(self, controller):
        '''
        writes cluster coordinate files based on the saved path and dataset selection information

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        controller.save_clusters(self.radio_select.get())
        self.on_tl_close(controller)
        
    def on_tl_close(self, controller):
        '''
        closes the frame

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.window.destroy()
        controller.save_frame = None
        
class grid_search_frame(object):
        
    def __init__(self, controller):
        '''
        generates the grid search frame which allows for running a grid search to identify optimal MORPHIOUS parameters

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        
        self.window = Toplevel()
        self.window.lift()
        
        self.window.title('Conduct a grid search to find optimal parameters')
        self.window.protocol('WM_DELETE_WINDOW', lambda : self.on_tl_close(controller))
        
        self.param_frame = LabelFrame(self.window, text='Step 1: Enter MORPHIOUS parameter ranges')
        self.param_frame.grid(row=0, column=0)
        
        self.nu_label = Label(self.param_frame, text="Enter values for Nu start, end, and total number of increments").grid(row=0, column=0)
        self.nu_input_start = Entry(self.param_frame, width=6)
        self.nu_input_end = Entry(self.param_frame, width=6)
        self.nu_input_incr = Entry(self.param_frame, width=6)
        
        self.nu_input_start.grid(row=0, column=1, padx=5)
        self.nu_input_end.grid(row=0, column=2, padx=5)
        self.nu_input_incr.grid(row=0, column=3, padx=5)
        
        #self.nu_label.insert(END, controller.nu_label)
        self.nu_input_start.insert(END, controller.nu_start)
        self.nu_input_end.insert(END, controller.nu_end)
        self.nu_input_incr.insert(END, controller.nu_incr)
        #self.nu_input.insert(END, controller.nu)
        
        self.gamma_label = Label(self.param_frame, text="Enter values for gamma start, end, and total number of increments").grid(row=1, column=0)
        self.gamma_input_start = Entry(self.param_frame, width=6)
        self.gamma_input_end = Entry(self.param_frame, width=6)
        self.gamma_input_incr = Entry(self.param_frame, width=6)
        
        self.gamma_input_start.grid(row=1, column=1, padx=5)
        self.gamma_input_end.grid(row=1, column=2, padx=5)
        self.gamma_input_incr.grid(row=1, column=3, padx=5)
        
        self.gamma_input_start.insert(END, controller.gamma_start)
        self.gamma_input_end.insert(END, controller.gamma_end)
        self.gamma_input_incr.insert(END, controller.gamma_incr)
        
        #self.gamma_input.insert(END, controller.gamma)
        
        self.minN_label = Label(self.param_frame, text="Enter values for minimum cluster size start, end, and total number of increments").grid(row=2, column=0)
        self.minN_input_start = Entry(self.param_frame, width=6)
        self.minN_input_end = Entry(self.param_frame, width=6)
        self.minN_input_incr = Entry(self.param_frame, width=6)
        
        
        self.minN_input_start.grid(row=2, column=1, padx=5)
        self.minN_input_end.grid(row=2, column=2, padx=5)
        self.minN_input_incr.grid(row=2, column=3, padx=5)
        
        self.minN_input_start.insert(END, controller.minN_start)
        self.minN_input_end.insert(END, controller.minN_end)
        self.minN_input_incr.insert(END, controller.minN_incr)
        
        #self.minN_input_end.insert(END, controller.minN)
        
        self.min_dist_label = Label(self.param_frame, text="Enter minimum distance").grid(row=3, column=0)
        self.min_dist_input = Entry(self.param_frame, width=6)
        self.min_dist_input.grid(row=3, column=1, padx=5)
        self.min_dist_input.insert(END, controller.min_dist)
        
        self.selection = IntVar()
        self.selection.set("1")
        
        self.features_button = Button(self.param_frame, text="Select Features", command=lambda : controller.open_feature_frame())
        self.features_button.grid(row=6, column=0, columnspan=2)
        
        
        #Panel #2 perform grid searches
        self.cv_frame = LabelFrame(self.window, text = "Step 2: generate cross-validation and test-set grid searches")
        self.cv_frame.grid(row=0, column=1)
        self.train_set_loaded = self.check_data_set_load(controller, train=True) # returns a label and sets radiobutton
        self.train_set_loaded.grid(row=0, column=1)
        
        self.cv_input = Entry(self.cv_frame, width=5)
        self.cv_input_label = Label(self.cv_frame, text="Enter # of cross validations").grid(row=2,column=1)
        self.cv_input.grid(row=2, column=2,padx=10)
        self.cv_input.insert(END, controller.cvs)
        
        self.test_set_loaded = self.check_data_set_load(controller, train=False) # returns a label and sets radiobutton
        self.test_set_loaded.grid(row=3, column=1, pady=10)
        
        self.output_button = Button(self.cv_frame, text="Select output directory", command=lambda : self.select_output_dir(controller))
        self.output_button.grid(row=5, column=1, columnspan=2)
        self.output_label = Label(self.cv_frame, text=controller.truncate_label_string(controller.gridsearch_output_path), relief=RIDGE, width=25)
        self.output_label.grid(row=6, column=1, columnspan=2)
        
        self.save_parameters = Button(self.cv_frame, text="Run!", command=lambda: self.grid_search(controller), padx=25, pady=5).grid(row=7, column=1, columnspan=3)
        
        self.optimal_param_frame = LabelFrame(self.window, text = "Step 3: determine optimal parameters")
        self.optimal_param_frame.grid(row=0, column=2)
        
        
        #Panel #3 find optimal grid search parameters
        self.cv_param_button = Button(self.optimal_param_frame, text="Selected CV dataset param file", command=lambda : self.select_param_file(controller, cv=True))
        self.cv_param_button.grid(row=0, column=2)
        self.cv_param_label = Label(self.optimal_param_frame, text=controller.truncate_label_string(controller.grid_cv_file), relief=RIDGE, width=25)
        self.cv_param_label.grid(row=1, column=2)
        
        self.test_param_button = Button(self.optimal_param_frame, text="Selected test dataset param file", command=lambda : self.select_param_file(controller, cv=False))
        self.test_param_button.grid(row=2, column=2)
        self.test_param_label = Label(self.optimal_param_frame, text=controller.truncate_label_string(controller.grid_test_file), relief=RIDGE, width=25)
        self.test_param_label.grid(row=3, column=2)
        
        self.output_button2 = Button(self.optimal_param_frame, text="Select output directory", command=lambda : self.select_output_dir(controller, sum_file=True))
        self.output_button2.grid(row=4, column=2)
        
        self.output_label2 = Label(self.optimal_param_frame, text=None, relief=RIDGE, width=25)
        self.output_label2.grid(row=5, column=2)
        
        self.summ_param_buttons = Button(self.optimal_param_frame,text="Generate Optimal Parameters File", command=lambda : controller.find_optimal_params())
        self.summ_param_buttons.grid(row=6, column=2)
        #buttons
        
    def select_param_file(self, controller, cv=True):
        '''
        select the CV or test dataset grid search parameter file to load for finding optimal parameters

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        cv : boolean, optional
            whether the selected file is the cross-validation set file. The default is True.

        Returns
        -------
        None.

        '''
        if cv:
            controller.grid_cv_file = filedialog.askopenfilename()
            
            self.cv_param_label.grid_remove()
            self.cv_param_label = Label(self.optimal_param_frame, text=controller.truncate_label_string(controller.grid_cv_file), relief=RIDGE, width=25)
            self.cv_param_label.grid(row=1, column=2)
            
        else:
            
            controller.grid_test_file = filedialog.askopenfilename()
            self.test_param_label.grid_remove()
            self.test_param_label = Label(self.optimal_param_frame, text=controller.truncate_label_string(controller.grid_test_file), relief=RIDGE, width=25)
            self.test_param_label.grid(row=3, column=2)
            
        
    def grid_search(self, controller):
        '''
        runs a grid search using the parameter information added by the user

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        
        controller.nu_start = self.nu_input_start.get()
        controller.nu_end = self.nu_input_end.get()
        controller.nu_incr = self.nu_input_incr.get()
        
        controller.gamma_start = self.gamma_input_start.get()
        controller.gamma_end = self.gamma_input_end.get()
        controller.gamma_incr = self.gamma_input_incr.get()
        
        controller.minN_start = self.minN_input_start.get()
        controller.minN_end = self.minN_input_end.get()
        controller.minN_incr = self.minN_input_incr.get()
        
        
        
        print(controller.nu_start, controller.nu_end, controller.nu_incr) 
        print(controller.gamma_start, controller.gamma_end, controller.gamma_incr) 
        print(controller.minN_start, controller.minN_end, controller.minN_incr) 
        
        print("radio selection: " + str(self.selection.get()))
        if(self.selection.get()==1):
            controller.cvs = int(self.cv_input.get())
            controller.grid_search(cv=True)
        elif(self.selection.get()==2):
            controller.grid_search(cv=False)
                
        #except:
            #print("Error! can only input numbers")
            
    def check_data_set_load(self,controller,train=True):
        '''
        checks where the training or test datasets are loaded

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        train : boolean, optional
            whether to check for the training dataset (True) or test data set. The default is True.

        Returns
        -------
        x : Tkinter label
            label indicating wether the selected dataset has been loaded.

        '''
        if train:
            loaded = False
            state = DISABLED
            if controller.train_df is not None:
                loaded = True
                state = NORMAL
            x = Label(self.cv_frame, text=f"train data loaded: {loaded}")
            
            Radiobutton(self.cv_frame, text="perform cross validation", variable=self.selection, value=1, state=state).grid(row=1,column=1)
        else:
            loaded = False
            state = DISABLED
            if controller.test_df is not None:
                loaded = True
                state = NORMAL
            x = Label(self.cv_frame, text=f"test data loaded: {loaded}")
            Radiobutton(self.cv_frame, text="use test set", variable=self.selection, value=2, state=state).grid(row=4,column=1, pady=0)
        return x
    
    def select_output_dir(self, controller, sum_file=False):
        '''
        select the directory where the grid search parameter or summary file should be written

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        sum_file : boolean, optional
            whether the summary file (True) or the parameter file (False) is being written. The default is False.

        Returns
        -------
        None.

        '''
        if sum_file:
            controller.summ_param_output_path = filedialog.askdirectory(initialdir="")
            self.set_output_label(controller, sum_file=sum_file)
            
        else:
            controller.gridsearch_output_path = filedialog.askdirectory(initialdir="")
            self.set_output_label(controller, sum_file=sum_file)
        self.window.lift()

    def set_output_label(self, controller, sum_file=False):
        '''
        generates a label for the selected output directory

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.
        sum_file : boolean, optional
            whether the output directory is for the summary file (True) or the grid search parameter file (False). The default is False.

        Returns
        -------
        None.

        '''
        if sum_file:
            self.output_label2.grid_remove()
            self.output_label2 = Label(self.optimal_param_frame, text=controller.truncate_label_string(controller.summ_param_output_path), relief=RIDGE, width=25)
            self.output_label2.grid(row=5, column=2)
            
        else:
            self.output_label.grid_remove()
            self.output_label = Label(self.cv_frame, text=controller.truncate_label_string(controller.gridsearch_output_path), relief=RIDGE, width=25)
            self.output_label.grid(row=6, column=1)
    
    def on_tl_close(self, controller):
        '''
        closes the frame

        Parameters
        ----------
        controller : controller object
            controller object to save information and navigate between GUI and morphious back-end.

        Returns
        -------
        None.

        '''
        self.window.destroy()
        controller.grid_search_frame = None
