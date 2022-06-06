/*
 * input directory should point to Iba1 images
 * 
 */

//v 2021-1-4


inputDir =  "your_path_here/microglia_sample_data/images/treatment/";
outputDir = "your_path_here/microglia_sample_data/features/treatment/cells/";
output_image_dir = "your_path_here/microglia_sample_data/features/treatment/cell_images/";
log_dir = "your_path_here/microglia_sample_data/features/treatment/logs/";


//microglia params
autolocalthreshold=false;
save_hyper_params = false;
parameter2=0;
batchmode=true;
erosion = 1; 
morpho_open1 = 0;
erosion2 = 0;
direct_filter = 6;
morpho_open2 = 2;
top = 150;

size = 30;
int_thresh="IJ_IsoData";

//correct image -- best not to modify
subtract = true;
subtract_by = "50";
despeckle = false; 
contrast = false;
contrast_by = "local_2.0"; //or, e.g., local_3.0 for local, or 0.3 for global contrast

count_microglia(inputDir, outputDir, output_image_dir, log_dir, batchmode, erosion, morpho_open1, erosion2, direct_filter, morpho_open2, top, size, autolocalthreshold, int_thresh, subtract, subtract_by, despeckle, contrast, contrast_by);


function count_microglia(inputDir, output_data_dir, output_image_dir, log_dir, batchmode, erosion, morpho_open, erosion2, direct_filter, morpho_open2, top_hat, size, autolocalthreshold, intensity_thresh, subtract, subtract_by, despeckle, contrast, contrast_by){
	print("accessed");
	setBatchMode(batchmode);

	run("Set Measurements...", "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction limit redirect=None decimal=3");
	run("Options...", "iterations=1 count=1 black");
	
	print("accessed main");
	
	threshold_path = "None";
	count=0;

	//autolocal threshold parameters
	method="Phansalkar";
	radius="60";
	parameter1 = "0";
	parameter2 = "0";
	
  	count=0;
	filelist = getFileList(inputDir);

	
	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
	output_subdir = "" + year + "-" + (month + 1) + "-" + dayOfMonth + "_" + hour + "h" + minute + "m" + second + "s";
	full_output_path = output_data_dir + "/" + output_subdir + "/";

	make_output_directory(full_output_path);
	

	logfile = File.open(log_dir+"/"+output_subdir+"_microglia_cellcounts_log.txt"); 
	print(logfile, "cell count log file");
	print(logfile, "erosion\t" + erosion);
	print(logfile, "morpho_open\t" + morpho_open);
	print(logfile, "erosion2\t" + erosion2);
	print(logfile, "direct_filter\t"	 + direct_filter);
	print(logfile, "morpho_open2\t" + morpho_open2);
	print(logfile, "top_hat\t" + top_hat);
	print(logfile, "parameter1\t" + parameter1);
	print(logfile, "parameter2\t" + parameter2);
	print(logfile, "size\t" + size);
	print(logfile, "autolocalthreshold\t" + autolocalthreshold);
	print(logfile, "intensity_thresh\t" + intensity_thresh);
	print(logfile, "subtract\t" + subtract);
	print(logfile, "subtract_by\t" + subtract_by);
	print(logfile, "despeckle\t" + despeckle);
	print(logfile, "contrast\t" + contrast);
	print(logfile, "contrast\t" + contrast_by);
	File.close(logfile);


	
	for(f=0;f < filelist.length; f++){
		file = filelist[f];
		full_path = inputDir+"/"+file;
		fn_len = parseInt(file.length());
		fname = substring(file, 0, (fn_len - 4)); //remove .tif for example

		print(full_path);
		open(full_path);
		area = create_background_selection();
		if( area > 0){
			correct_image(subtract, subtract_by, despeckle, contrast, contrast_by);


			
			custom_morphological_filtering3(erosion, morpho_open, erosion2, direct_filter, morpho_open2, top_hat);
			
			if (autolocalthreshold){
				autolocal_threshold(method,radius,parameter1,parameter2);
			} else {
				intensity_threshold(threshold_path,intensity_thresh,0);
			}
			run("Make Binary");
			run("Analyze Particles...", "size="+size+"-Infinity display clear include add");
			print("... analyzed particles complete ...");
	
			print("======================");
			print(outputDir);
			print("======================");
			save_image(output_image_dir, fname);
			save_data(full_output_path, fname);
			
		} else {
			nCells = 0;
		}
		reset_();
	}
	setBatchMode(false);
}

function custom_morphological_filtering3(erosion,morpho_open,erosion2,direct_filter,morpho_open2,top_hat){
	if(erosion > 0){
		run("Morphological Filters", "operation=Erosion element=Octagon radius="+toString(erosion));
	}
	if (morpho_open > 0){
		run("Morphological Filters", "operation=Opening element=Octagon radius="+toString(morpho_open));
		print("morpho_open1 "+toString(morpho_open));
	} if (erosion2 > 0){
		run("Gray Scale Attribute Filtering", "operation=Opening attribute=Area minimum="+toString(gray_open)+" connectivity=8");
		print("gray_open "+toString(gray_open));
	} if (direct_filter > 0){
		run("Directional Filtering", "type=Max operation=Mean line="+toString(direct_filter)+" direction=32");
		print("direct_filter "+toString(direct_filter));
	} if (morpho_open2 > 0){
		run("Morphological Filters", "operation=Opening element=Octagon radius="+toString(morpho_open2));
		print("morpho_open2 "+toString(morpho_open2));
	} if (top_hat > 0) {
		run("Gray Scale Attribute Filtering", "operation=[Top Hat] attribute=[Box Diagonal] minimum="+toString(top_hat)+" connectivity=4");
		print("top_hat "+toString(top_hat));
	}
}

function autolocal_threshold(method,radius,parameter1,parameter2){
	run("8-bit");
	print(method);
	print(radius);
	print(parameter1);
	print(parameter2);
	run("Auto Local Threshold", "method="+method+" radius="+radius+" parameter_1="+parameter1+" parameter_2="+parameter2+" white");
}

function intensity_threshold(threshpath,threshtype,roi){
	if(threshpath == "None"){
		if(toString(roi) == "None"){
			run("Select None");
		} else {
			roiManager("Select", roi);
		}
		setAutoThreshold(threshtype+" dark");
	} else {
		print(threshpath);
		F=File.openAsString(threshdir+"\\"+file+".txt");
		getMinAndMax(min,max);
		lower_upper=split(F,"_");
		setThreshold(lower_upper[0],max+1);
	}
}

function correct_image(subtract,subtract_by,despeck,contrast,contrast_by){
	if(contrast == true){
		if (indexOf(contrast_by, "local") >= 0) {
		//if((contrast_by == "local")==true){
			info = split(contrast_by, "_");
			contrast_by_value = info[1];
			print("local contrast by..",contrast_by_value);
			run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum="+contrast_by_value+" mask=*None* fast_(less_accurate)");
		} else {
			run("Enhance Contrast...", "saturated="+contrast_by+" normalize");
		}
	}
		
	if(subtract == true){
		run("Subtract Background...", "rolling="+subtract_by);
	}
	if(despeck == true){
		run("Despeckle");	
	}
}

function save_image(output, filename){
	saveAs("Tiff", output+"/"+filename+".tif");
}

function save_data(output, filename){
	data_output = output + "/data/";
	roi_output = output + "/rois/";
	make_output_directory(data_output);
	make_output_directory(roi_output);
	
	selectWindow("Results");
	saveAs("Results", data_output+"/"+filename+".txt");
	save_rois(roi_output, filename);
}

function reset_(){
	clear_roi_manager();
	close_windows();
	run("Clear Results");
	collectGarbageIfNecessary();
}

function close_windows(){
	while (nImages>0) { 
          selectImage(nImages); 
          close(); 
     }
}

function clear_roi_manager(){
	array1 = newArray();
	print(roiManager("count"));
	for (i=0;i<roiManager("count");i++){ 
        array1 = Array.concat(array1,i); 
	} 
	roiManager("select", array1); 
	roiManager("Delete");
}

function save_rois(outputDir,fname){
	array1 = newArray();
	print(roiManager("count"));
	for (i=0;i<roiManager("count");i++){ 
        array1 = Array.concat(array1,i); 
	} 
	roiManager("select", array1); 
	roiManager("Save", outputDir+"/"+fname+".zip");
}

function set_window(fname){
	toselect=fname+"-attrFilt-attrFilt"; //for v2
	selectWindow(toselect);
	roiManager("Select", 0);
}

function create_background_selection(){
	getStatistics(area_check);
	if(area_check > 0){
		run("Select None");
		getMinAndMax(min,max);
		setThreshold(1, max+1);
		run("Create Selection");
		getStatistics(area, mean);
		roiManager("add");
	} else{
		area = 0;
	}
	
	return area;
}

function make_output_directory(outputpath){
	if (!File.exists(outputpath)){
			File.makeDirectory(outputpath);
		}
}



//Global variables
var collectGarbageInterval = 3; // the garbage is collected after n Images
var collectGarbageCurrentIndex = 1; // increment variable for garbage collection
var collectGarbageWaitingTime = 100; // waiting time in milliseconds before garbage is collected
var collectGarbageRepetitionAttempts = 1; // repeats the garbage collection n times
var collectGarbageShowLogMessage = true; // defines whether or not a log entry will be made

//Functions

//-------------------------------------------------------------------------------------------
// this function collects garbage after a certain interval
//-------------------------------------------------------------------------------------------
function collectGarbageIfNecessary(){
	if(collectGarbageCurrentIndex == collectGarbageInterval){
	setBatchMode(false);
	wait(collectGarbageWaitingTime);
	for(i=0; i<collectGarbageRepetitionAttempts; i++){
	wait(100);
	//run("Collect Garbage");
	call("java.lang.System.gc");
	}
	if(collectGarbageShowLogMessage) print("...Collecting Garbage...");
	collectGarbageCurrentIndex = 1;
	setBatchMode(true);
	} else collectGarbageCurrentIndex++;
}
