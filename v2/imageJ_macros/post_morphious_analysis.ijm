/*
 * measures immunofluorescence, skeleton, and cellular features for microglia and astrocytes
 * used for both whole sections and MORPHIOUS clusters
 *  
 */

//v 2022-2-12

input_dir = "/PATH TO INPUT FILES/";
output_dir = "/PATH TO AN OUTPUT DIRECTORY/";

//analyses
process_skeleton=true;
skeleton_dir = "/PATH TO SKELETONIZED IMAGES/";

process_cell=true;
cell_dir = "/PATH TO BINARY CELL IMAGES/";
cell_size_thresh=30; //keep the same as the size parameter in the count_microglia or count_astrocyte macros

//name the directory within "output_dir" to save the analysis. If left empty, default output directory names are chosen
override_save_dir_name = ""; 

perform_cluster_analysis=true; // if false, runs analysis on the whole image
roi_dir = "/PATH TO CLUSTER ROIs/";

//if distal_procedure is true, subtracts the outside of a cluster region to analyze the distal region, takes priority over proximal_from_combined_procedure
distal_procedure=false; 

proximal_from_combined_procedure=false; //if true, removes an inner cluster region from an outer cluster region
remove_inner_cluster_dir = "/PATH TO INNER CLUSTER REGION (e.g., focal)/";


//preprocessing settings
image_processing=false; //set to true to preprocess image
//ignored if image_processing is set to false
subtract = true; 
subtract_by = "100";
contrast = true;
contrastby="local_2.0"; //use local_{some number}, e.g., local_2.0 to use local contrast
despeckle = true;

batchmode=true;


// user parameters stops
main(batchmode, input_dir, output_dir, skeleton_dir, roi_dir, cell_dir, cell_size_thresh, perform_cluster_analysis, process_skeleton, process_cell, image_processing, subtract,subtract_by,contrast,contrastby,despeckle, distal_procedure, proximal_from_combined_procedure, remove_inner_cluster_dir);

//Global variables
var collectGarbageInterval = 2; // the garbage is collected after n Images
var collectGarbageCurrentIndex = 1; // increment variable for garbage collection
var collectGarbageWaitingTime = 100; // waiting time in milliseconds before garbage is collected
var collectGarbageRepetitionAttempts = 2; // repeats the garbage collection n times
var collectGarbageShowLogMessage = true; // defines whether or not a log entry will be made

function main(batchmode, input_dir, output_dir, skel_dir, roi_path, cell_dir, cell_size_thresh, perform_cluster_analysis, process_skeleton, process_cell, image_processing, subtract, subtract_by, contrast, contrastby, despeckle, distal_procedure, proximal_from_combined_procedure, remove_inner_cluster_dir){
	setBatchMode(batchmode);
	autolocal=true;
	local_thresh_type = "Phansalkar";
	radius = 60;

	default_area_threshold=100;

	if (parseInt(lengthOf(override_save_dir_name)) > 0){
		cluster = override_save_dir_name;
	} else if (perform_cluster_analysis == false){
		cluster="whole_image";
	} else if(distal_procedure){
		cluster = "distal";
	} else if (proximal_from_combined_procedure){
		cluster="proximal_from_combined";
	} else {
		if(indexOf(roi_path, "/") > -1){
			info = split(roi_path, "/");
			cluster=info[info.length-1];
		} else {
			cluster = "default";
		}
	}

	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
	time_string = ""+year+"_"+(month+1)+"_"+dayOfMonth+"_"+hour+"h"+minute+"m"+second+"s";
	cluster = cluster + "_" + time_string;

	File.makeDirectory(output_dir+"/" + cluster + "/");
	IF_output_dir = output_dir + "/" + cluster + "/IF_data";
	File.makeDirectory(IF_output_dir);

	logfile = File.open(output_dir+"/"+cluster+"/log.txt"); 
	print(logfile, "post-MORPHIOUS analysis log file");
	print(logfile, "input image path\t" + input_dir);
	print(logfile, "output path\t" + output_dir);
	print(logfile, "input skeleton path\t" + skel_dir);
	print(logfile, "input ROI path\t" + roi_path);
	print(logfile, "input cell path\t" + cell_dir);
	print(logfile, "cell size threshold\t" + cell_size_thresh);
	print(logfile, "perform cluster analysis\t" + perform_cluster_analysis);
	print(logfile, "perform skeleton analysis\t" + process_skeleton);
	print(logfile, "perform cell analysis\t" + process_cell);
	print(logfile, "get distal region\t" + distal_procedure);
	print(logfile, "subtract inner from outer cluster region\t" + proximal_from_combined_procedure);
	print(logfile, "inner region to subtract\t" + remove_inner_cluster_dir);
	print(logfile, "preprocess images\t" + image_processing);
	print(logfile, "subtract background\t" + subtract);
	print(logfile, "subtract backround amount\t" + subtract_by);
	print(logfile, "apply contrast\t" + contrast);
	print(logfile, "contrast amount\t" + contrastby);
	print(logfile, "apply despeckling\t" + despeckle);
	File.close(logfile);

	if(process_skeleton){
		skeleton_output_dir = output_dir + "/" + cluster + "/skeleton_data/";
		File.makeDirectory(skeleton_output_dir);
	}

	if(process_cell){
		cell_output_dir = output_dir + "/" + cluster + "/cell_data/";
		File.makeDirectory(cell_output_dir);
	}
	
	imgs = getFileList(input_dir);
	Array.print(imgs);

	for(i=0; i<imgs.length; i++){
		f = imgs[i];
		print(f);
		fn_len = parseInt(lengthOf(f));
		fn = substring(f, 0, (fn_len - 4)); //remove .tif for example
		roi = fn + ".roi";
		txt_file = fn + ".txt";

		//set file paths

		full_img_path = input_dir+"/"+f;
		// open image and preprocess if necessary
		open(full_img_path);
		img_bg_area = background_measure();
		if (image_processing){
			process_image(subtract,subtract_by,contrast,contrastby,despeckle);
		}
		
		perform_analysis=false;
		if (perform_cluster_analysis){
			// open cluster rois
			cluster_roi_path = roi_dir + "/" + roi;
			//set path for inner cluster to remove from outer cluster. only applicable for proximal_from_combined_procedure
			inner_cluster_path = remove_inner_cluster_dir + "/" + roi; 
			
			//check if rois exist and clear non-relevant areas
			perform_analysis = perform_cluster_segmentation(cluster_roi_path, distal_procedure, proximal_from_combined_procedure, inner_cluster_path);
			area_threshold=0;
			//if cluster roi exists, measure background area
			if (perform_analysis){
				cluster_bg_area = background_measure();
				if(cluster_bg_area > default_area_threshold){ //check if sufficient area for analysis
					perform_analysis=true;
				}
			}
		} else{
			cluster_bg_area = 0;
			if(img_bg_area > default_area_threshold){
				perform_analysis=true;
			}
		}
		
		//perform IF analysis if area sufficiently large and it meets the perform analysis criteria
		if(perform_analysis){
			autolocal_threshold_measure(local_thresh_type,radius);
			setResult("ImageBackgroundArea", 0, img_bg_area);
			setResult("ClusterBackgroundArea", 0, cluster_bg_area);
			updateResults();
			save_results(IF_output_dir,txt_file);
			run("Clear Results");
		}
		reset_all();
		
		if(process_skeleton){
			if(perform_analysis){
				full_skel_path = skel_dir+"/"+f;
				open(full_skel_path);
				if(perform_cluster_analysis){
					_ = perform_cluster_segmentation(cluster_roi_path, distal_procedure, proximal_from_combined_procedure, inner_cluster_path);
				}
				run("Analyze Skeleton (2D/3D)", "prune=none show");
				setResult("ImageBackgroundArea", 0, img_bg_area);
				setResult("ClusterBackgroundArea", 0, cluster_bg_area);
				updateResults();
				save_skeleton(skeleton_output_dir, fn);
				reset_all();
				collectGarbageIfNecessary();
			}
			reset_all();
		}

		if(process_cell){
			if(perform_analysis){
				full_cell_path = cell_dir+"/"+f;
				open(full_cell_path);
				if (perform_cluster_analysis){
					_ = perform_cluster_segmentation(cluster_roi_path, distal_procedure, proximal_from_combined_procedure, inner_cluster_path);
				}
				count_cells(cell_size_thresh);
				setResult("ImageBackgroundArea", 0, img_bg_area);
				setResult("ClusterBackgroundArea", 0, cluster_bg_area);
				updateResults();
				save_results(cell_output_dir,txt_file);
				reset_all();
				collectGarbageIfNecessary();
			}
			reset_all();
		}
	}
}

function perform_cluster_segmentation(cluster_roi_path, distal_procedure, proximal_from_combined, inner_cluster_path){
	if(distal_procedure){
		if(File.exists(cluster_roi_path)){
			segment_by_cluster(cluster_roi_path, false); //clears cluster area leaving distal area
		}
		perform_analysis=true; //still analyze as distal even without cluster area
	} else {
		if(File.exists(cluster_roi_path)){
			segment_by_cluster(cluster_roi_path, true); //clears outside cluster area
			if(proximal_from_combined_procedure){
				if(File.exists(inner_cluster_path)){
					segment_by_cluster(inner_cluster_path, false); //clears cluster area
				}
			}
			perform_analysis=true;
		} else {
			perform_analysis=false;
		}
	}
	return perform_analysis;
}


function process_image(subtract,subtract_by,contrast,contrastby,despeckle){
	if(contrast == true){
		if (indexOf(contrastby, "local") >= 0) {
			//if((contrast_by == "local")==true){
			info = split(contrastby, "_");
			contrast_by_value = info[1];
			print("local contrast by..",contrast_by_value);
			run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum="+contrast_by_value+" mask=*None* fast_(less_accurate)");
		} else {
			run("Enhance Contrast...", "saturated="+contrastby+" normalize");
			print("global contrast...");
		}
	}
	
	if(subtract == true){
		run("Subtract Background...", "rolling="+subtract_by);
	}
	if(despeckle == true){
		run("Despeckle");	
	}
}

function segment_by_cluster(cluster_roi_path, clear_outside){
	roiManager("open", cluster_roi_path);
	nrois = roiManager("count");
	roiManager("select", nrois-1);
	if(clear_outside){
		run("Clear Outside");
	} else {
		run("Clear");
	}	
}

function background_measure(){
	run("Select None");
	getMinAndMax(min,max);
	setThreshold(1, max+1);
	bg_area = getValue("Area limit");
	resetThreshold();
	return bg_area;
}

function autolocal_threshold(threshtype,radius){
	run("Select All");
	run("Duplicate...", "title=1");
	run("Duplicate...", "title=2");
	selectWindow("1");
	thresh = threshtype;
	run("8-bit");
	run("Auto Local Threshold", "method="+threshtype+" radius="+radius+" parameter_1=0 parameter_2=0 white");
	run("Create Selection");
	roiManager("Add");
}

function autolocal_threshold_measure(thresh,radius){
	autolocal_threshold(thresh,radius); //adds an roi
	selectWindow("2");
	nrois = roiManager("count");
	roiManager("select", nrois-1); //analyze the last one
	roiManager("measure");
}


function clear_roi_manager(){
	if (roiManager("count") > 0){
		roiManager("deselect");
		roiManager("Delete");
	}
}

function close_windows(){
	while (nImages>0) { 
          selectImage(nImages); 
          close(); 
    }
	list = getList("window.titles"); 
	for (i=0; i<list.length; i++){ 
	winame = list[i]; 
		selectWindow(winame); 
	run("Close"); 
	} 
}

function reset_all(){
	run("Clear Results");
	clear_roi_manager();
	close_windows();
}


function save_results(path,file){
	print("saving data!");
	saveAs("Results", path+"/"+file);
	print("data saved");
}

function save_skeleton(path,fname){
	selectWindow("Branch information");
	saveAs("Results", path+"/"+fname+"_branchInfo.txt");
	selectWindow("Results");
	saveAs("Results", path+"/"+fname+"_rawInfo.txt");
}

function count_cells(size){
	nrois = roiManager("count");
	if(nrois>0){
		roiManager("Deselect");
		roiManager("Delete");
	}
	run("Select None");
	run("Remove Overlay");
	setThreshold(1, 255);
	//run("Make Binary");
	run("Analyze Particles...", "size="+size+"-Infinity display clear include add");
	print("... analyzed particles complete ...");
}

//Functions

//-------------------------------------------------------------------------------------------
// this function collects garbage after a certain interval
//-------------------------------------------------------------------------------------------
function collectGarbageIfNecessary(){
	if(collectGarbageCurrentIndex == collectGarbageInterval){
		//setBatchMode(false);
		wait(collectGarbageWaitingTime);
		for(i=0; i<collectGarbageRepetitionAttempts; i++){
			wait(100);
			//run("Collect Garbage");
			call("java.lang.System.gc");
		}
		if(collectGarbageShowLogMessage) print("...Collecting Garbage...");
		collectGarbageCurrentIndex = 1;
		//setBatchMode(true);
	}	else collectGarbageCurrentIndex++;
}
