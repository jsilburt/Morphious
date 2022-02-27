
/*
 * InputDir should point to the directory with the s100b image files
 */

inputDir =  "your_path_here/microglia_sample_data/images/treatment/";
outputDir = "your_path_here/microglia_sample_data/features/treatment/cells/";
output_image_dir = "your_path_here/microglia_sample_data/features/treatment/cell_images/";
log_dir = "your_path_here/microglia_sample_data/features/treatment/logs/";

batchmode=true;
morpho_open1 = 2; 
gray_open = 100; 
direct_filter = 10;
morpho_open2 = 0;
top_hat = true;
parameter1 = -1;
parameter2 = 0;
size=30;

subtract = true;
subtract_by = "50";
despeckle = false; 
contrast = false;
contrast_by = "local_2.0";


autolocalthreshold=true;

count_astrocytes(inputDir, outputDir, output_image_dir, log_dir, batchmode, morpho_open1, gray_open, direct_filter, morpho_open2, top_hat, parameter1,parameter2,size,autolocalthreshold, subtract, subtract_by, despeckle, contrast, contrast_by);

//code starts here
function count_astrocytes(inputDir, outputDir, output_image_dir, log_dir, batchmode, morpho_open, gray_open, direct_filter, morpho_open2, top_hat, parameter1, parameter2, size, autolocalthreshold, subtract, subtract_by, despeckle, contast, contrast_by){
	setBatchMode(batchmode);

	run("Set Measurements...", "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction limit redirect=None decimal=3");
	run("Options...", "iterations=1 count=1 black");
	
	intensity_thresh="IJ_IsoData";
	method="Phansalkar";
	radius="60";
	
	filelist = getFileList(inputDir);

	
	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
	output_subdir = "" + year + "-" + (month + 1) + "-" + dayOfMonth + "_" + hour + "h" + minute + "m" + second + "s";
	full_output_path = outputDir + "/" + output_subdir + "/";

	make_output_directory(full_output_path);
	

	logfile = File.open(log_dir+"/"+output_subdir+"astrocyte_cellcounts_log.txt"); 
	print(logfile, "cell count log file");
	print(logfile, "morpho_open\t" + morpho_open);
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
	print(logfile, "contrast_by\t" + contrast_by);
	File.close(logfile);
	
	for(f=0;f < filelist.length; f++){
		file = filelist[f];
		full_path = inputDir+"/"+file;

		fn_len = parseInt(file.length());
		fname = substring(file, 0, (fn_len - 4)); //remove .tif for example

		print(full_path);
		open(full_path);
		area = create_background_selection();
		correct_image(subtract, subtract_by, despeckle, contrast, contrast_by);
		custom_morphological_filtering(morpho_open, gray_open, direct_filter, morpho_open2, top_hat);
		
		if (autolocalthreshold){
			autolocal_threshold(method,radius,parameter1,parameter2);
		} else {
			intensity_threshold(threshold_path,intensity_thresh, 0);
		}

		run("Make Binary");
		run("Analyze Particles...", "size="+size+"-Infinity display clear include add");

		print("... analyzed particles complete ...");
		save_image(output_image_dir, fname);
		save_data(full_output_path, fname);
		reset_();
	}
	setBatchMode(false);
}


function custom_morphological_filtering(morpho_open,gray_open,direct_filter,morpho_open2,top_hat){
	if (morpho_open > 0){
		run("Morphological Filters", "operation=Opening element=Octagon radius="+toString(morpho_open));
		print("morpho_open1 "+toString(morpho_open));
	} if (gray_open > 0){
		run("Gray Scale Attribute Filtering", "operation=Opening attribute=Area minimum="+toString(gray_open)+" connectivity=8");
		print("gray_open "+toString(gray_open));
	} if (direct_filter > 0){
		run("Directional Filtering", "type=Max operation=Mean line="+toString(direct_filter)+" direction=32");
		print("direct_filter "+toString(direct_filter));
	} if (morpho_open2 > 0){
		run("Morphological Filters", "operation=Opening element=Octagon radius="+toString(morpho_open2));
		print("morpho_open2 "+toString(morpho_open2));
	} if (top_hat) {
		run("Gray Scale Attribute Filtering", "operation=[Top Hat] attribute=Area minimum=500 connectivity=8");
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

function save_image(output, filename){
	saveAs("Tiff", output+"/"+filename+".tif");
}

function save_data(output, filename){
	data_output = output + "/data/";
	roi_output = output + "/rois/";
	make_output_directory(data_output);
	make_output_directory(roi_output);
	
	selectWindow("Results");
	saveAs("Results", data_output+filename+".txt");
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
	roiManager("Save", outputDir+fname+".zip");
}

function open_image(file,filepath,threshold_path){
	open(filepath+"\\"+file);
	selectWindow(file);
	if(threshold_path == "None"){
		roiManager("Add");
	}
}

function set_window(fname){
	toselect=fname+"-attrFilt-attrFilt"; //for v2
	selectWindow(toselect);
	roiManager("Select", 0);
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
