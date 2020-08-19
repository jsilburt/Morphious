print("accessed cell count macro");
print("This macro will count microglia or astrocyte cell bodies");
print("specify image directories and output directories");
print("the output directory should contain subfolders for: /counts/, /rois/, /image/");


//COUNT ASTROCUTES

batchmode=true;
morpho_open1 = 2; 
gray_open = 100; 
direct_filter = 10;
morpho_open2 = 0;
top_hat = true;
parameter1 = -1;
parameter2 = 0;
size=30;
save_roi=true;
save_hyper_params=false;
autolocalthreshold=true;



_dir = "G";
/*
 * InputDir should point to the directory with the s100b image files
 */
inputDir = "G:/lab_files/imageJ_macro_working_directory/Gfap_S100b_Nestin/input_s100b_all_v6--one-model/";


/*
 * outputDir should point to a directory that contains the following folders:
 * /counts/
 * /image/
 * /rois/
 */
outputDir = "G:/lab_files/imageJ_macro_working_directory/Gfap_S100b_Nestin/output/set4_one_model/feature_files/single_threshold/count_data/";

batchmode=false;
morpho_open1 = 2; 
gray_open = 100; 
direct_filter = 10;
morpho_open2 = 0;
top_hat = true;
parameter1 = -1;
parameter2 = 0;
size=30;
save_roi=true;

autolocalthreshold=true;


//count_astrocytes(batchmode, morpho_open1, gray_open, direct_filter, morpho_open2, top_hat, parameter1,parameter2,size,autolocalthreshold,save_roi,inputDir, outputDir);



//microglia params

autolocalthreshold=false;
save_roi = true;
save_hyper_params = false;
parameter2=0;
batchmode=true;
erosion = 1; 
morpho_open1 = 0;
erosion2 = 0;
direct_filter = 6;
morpho_open2 = 2;
top = 150;

parameter1 = 0;
parameter2 = 0;
size = 40; //used to be 25 -- switched to 40 when local contrast used
int_thresh="IJ_IsoData";


dir="G";


inputDir = "";
outputDir = "";

batchmode = false;

//count_microglia(inputDir, outputDir, batchmode, erosion, morpho_open1, erosion2, direct_filter, morpho_open2, top, parameter1,parameter2,size,autolocalthreshold,int_thresh,save_roi);




//code starts here
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

function save_image(filename,output){
	filename = replace(filename,".tif","");
	saveAs("Tiff", output+"/image/"+filename+".tif");
	selectWindow("Results");
	saveAs("Results", output + "\\counts\\"+filename + ".txt");
	save_rois(output+"\\rois\\",filename);
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

function correct_image(subtract,subtract_amount,despeck,contrast){
	if(indexOf(contrast, "local")>0){
		info = split("contrast","_");
		contrastby = info[1];
		run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum="+contrastby+" mask=*None* fast_(less_accurate)");
	}
	if(subtract == true){
		run("Subtract Background...", "rolling="+subtract_amount);
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


//for astrocytes
function count_astrocytes(batchmode, morpho_open, gray_open, direct_filter, morpho_open2, top_hat, parameter1, parameter2, size, autolocalthreshold, save_roi,
inputDir, outputDir){
	setBatchMode(batchmode);

	run("Set Measurements...", "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction limit redirect=None decimal=3");

	process_image = true;
	subtract = true;
	subtract_amount = "50";
	despeckle = false; 
	contrast = false; 
	intensity_thresh="IJ_IsoData";

	method="Phansalkar";
	radius="60";
	
	filelist = getFileList(inputDir);
	
	for(f=0;f < filelist.length; f++){
		file = filelist[f];
		full_path = inputDir+file;

		print(full_path);
		open(full_path);
		area = create_background_selection();

		if (process_image){
			correct_image(subtract, subtract_amount, despeckle, contrast);
		}
		fname = replace(file,".tif","");

		custom_morphological_filtering(morpho_open, gray_open, direct_filter, morpho_open2, top_hat);
		
		if (autolocalthreshold){
			autolocal_threshold(method,radius,parameter1,parameter2);
		} else {
			intensity_threshold(threshold_path,intensity_thresh,0);
		}

		run("Make Binary");
		run("Analyze Particles...", "size="+size+"-Infinity display clear include add");

		print("... analyzed particles complete ...");

		if (save_roi){
			save_image(file,outputDir);
		}
		reset_();
	}
	setBatchMode(false);
}


//for microglia
function count_microglia(inputDir, outputDir, batchmode, erosion, morpho_open, erosion2, direct_filter, morpho_open2, top_hat, parameter1, parameter2, size, autolocalthreshold, intensity_thresh, save_roi){
	setBatchMode(batchmode);

	run("Set Measurements...", "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction limit redirect=None decimal=3");
	print("accessed main");
	
	threshold_path = "None";
	count=0;

	//only subtract background for counting cells
	process_image = true;
	subtract = true;
	subtract_amount = "50";
	despeckle = true; 
	contrast = false;

	parameter1="0";
	parameter2="0"; // do not touch unless necessary

	//autolocal threshold parameters
	method="Phansalkar";
	radius="60";
	
  	count=0;
	filelist = getFileList(inputDir);


	logfile = File.open(outputDir+"/log.txt"); 
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
	print(logfile, "subtract_amount\t" + subtract_amount);
	print(logfile, "despeckle\t" + despeckle);
	print(logfile, "contrast\t" + contrast);
	File.close(logfile);
	
	for(f=0;f < filelist.length; f++){
		file = filelist[f];
		full_path = inputDir+file;

		print(full_path);
		open(full_path);
		area = create_background_selection();
		if( area > 0){
			if (process_image){
				correct_image(subtract, subtract_amount, despeckle, contrast);
			}
			fname = replace(file,".tif","");
			custom_morphological_filtering3(erosion, morpho_open, erosion2, direct_filter, morpho_open2, top_hat);
			
			if (autolocalthreshold){
				autolocal_threshold(method,radius,parameter1,parameter2);
			} else {
				intensity_threshold(threshold_path,intensity_thresh,0);
			}
			run("Make Binary");
			run("Analyze Particles...", "size="+size+"-Infinity display clear include add");
			print("... analyzed particles complete ...");
	
			if (save_roi){
				print("======================");
				print(outputDir);
				print("======================");
				save_image(file,outputDir);
			}
			
		} else {
			nCells = 0;
		}
		reset_();
	}
	setBatchMode(false);
}


function set_threshold(file,threshdir){
	print(threshdir+"\\"+file);
	F=File.openAsString(threshdir+"\\"+file+".txt");
	getMinAndMax(min,max);
	lower_upper=split(F,"_");
	setThreshold(lower_upper[0],max);
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
