print("this performs immunofluorescence and skeleton analysis to an image");
print("the input_dir should point to the input images");
print("the outputdir should point to an outpout folder that has /IF_data/ and /skeleton_data/ as subdirectories");


input_dir = "";
output_dir = "";
batchmode = true


main(input_dir, output_dir, batchmode);

function main(input_dir, output_dir, batchmode){
	setBatchMode(batchmode);
	
	autolocal=true;
	local_thresh_type = "Phansalkar"; //"Phansalkar"; //Niblack for microglia
	radius = 60;
	subtract = true; //subtract background
	subtract_by = "100"; // amount to subtract by -- input as string for imageJ to interpret
	despeckle = true; // apply 1 round of despeckling
	contrast = false;
	

	process_skeleton=true;
	
	cell_roi_dir = "";
	cutout_cell_bodies=false;
	cross_cell_filename=false;
	from_cell="gfap";
	to_cell="s100b";


	imagefiles = getFileList(input_dir);
	Array.print(imagefiles);


	for(j=0;j<imagefiles.length;j++){
		img_file=imagefiles[j];
		txt_file=replace(img_file,"tif","txt");
		fname = replace(img_file,"tif","");
		print(fname);
		//process IF data
		open(input_dir+"/"+img_file);
		
		process_image(subtract,subtract_by,contrast,despeckle);
		if(roiManager("count") > 0){
			clear_roi_manager();
		}

		background_measure();
		threshold_measure(autolocal,local_thresh_type,radius);

		save_results(output_dir,"/IF_data/",txt_file);
		run("Clear Results");

		//process skeleton data
		if(process_skeleton){
			area_metrics = calculate_percArea(0);
			percArea = area_metrics[0];
			fore = area_metrics[1];
			back = area_metrics[2];
			print(fore);
			print(back);
			
			selectWindow("1");
			run("Select All");
			
			if(cutout_cell_bodies){
				if(cross_cell_filename){
					cell_fname = replace(fname,from,to);					
				}
				else{
					cell_fname = fname;
				}
				cell_roi_path = cell_roi_dir + "/" + cell_fname+"zip";
				clear_cell_bodies("1",cell_roi_path);
			}

			skeleton_analysis();
			selectWindow("Results");
			setResult("percArea", 0, percArea);
			setResult("Area", 0, fore);
			setResult("backgroundArea", 0, back);
			updateResults();
	
			save_skeleton(output_dir+"/skeleton_data/",fname);
		}
		
		reset_all();
		collectGarbageIfNecessary();
		collectGarbageIfNecessary();
	}
}


function process_file_check(file, ID_checklist){
	pass = false;
	for(z=0;z<ID_checklist.length;z++){
		ref_ID = ID_checklist[z];
		info = split(file,"_");
		ID = info[0];
		if(ID == ref_ID){
			pass = true;
		}
	}
	return pass;
}

function process_image(subtract,subtract_by,contrast,despeckle){
	if(contrast == true){
		run("Enhance Contrast...", "saturated=0.3 normalize");
		print("global contrast...");
	}
	if (indexOf(contrast, "local") >= 0) {
		//if((contrast_by == "local")==true){
		info = split(contrast, "_");
		contrast_by_value = info[1];
		print("local contrast by..",contrast_by_value);
		run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum="+contrast_by_value+" mask=*None* fast_(less_accurate)");
	}
	
	if(subtract == true){
		run("Subtract Background...", "rolling="+subtract_by);
	}
	if(despeckle == true){
		run("Despeckle");	
	}
}


function background_measure(){
	getMinAndMax(min,max);
	setThreshold(1, max+1);
	run("Measure");
	resetThreshold();
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

function threshold_measure(autolocal,thresh,radius){
	if(autolocal){
		autolocal_threshold(thresh,radius);
		selectWindow("2");
		roiManager("select",0);
		roiManager("measure");
	} else {
		print("error... non-autolocalthreshold not implemented");
	}
}

function calculate_percArea(roiID){
	run("Select All");
	getMinAndMax(min, max);
	setThreshold(1, max+1);
	run("Measure");
	back = getResult("Area",0);
	resetThreshold();
	roiManager("select",roiID);
	run("Measure");
	fore = getResult("Area",1);
	percArea = fore/back;
	print(percArea);
	run("Clear Results");
	return newArray(percArea, fore, back);
}

function skeleton_analysis(){
	selectWindow("1");
	print("skeletonizing");
	run("Skeletonize (2D/3D)");
	print("analyze skeletons");
	run("Analyze Skeleton (2D/3D)", "prune=none show");
	print("completed analysis");
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


function save_results(dir,extra,file){
	print("saving data!");
	saveAs("Results", dir+"/"+extra+"/"+file);
	print("data saved");
}

function save_skeleton(path,fname){
	selectWindow("Branch information");
	saveAs("Results", path+"/"+fname+"_branchInfo.txt");
	selectWindow("Results");
	saveAs("Results", path+"/"+fname+"_rawInfo.txt");
}

function clear_cell_bodies(window, cell_roi_path){
	clear_roi_manager();
	selectWindow(window);
	roiManager("Open", cell_roi_path);
	for(i=0; i < roiManager("count"); i++){
		roiManager("select",i);
		run("Clear");
	}
	clear_roi_manager();
}


//Global variables
var collectGarbageInterval = 2; // the garbage is collected after n Images
var collectGarbageCurrentIndex = 1; // increment variable for garbage collection
var collectGarbageWaitingTime = 100; // waiting time in milliseconds before garbage is collected
var collectGarbageRepetitionAttempts = 2; // repeats the garbage collection n times
var collectGarbageShowLogMessage = true; // defines whether or not a log entry will be made

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
}else collectGarbageCurrentIndex++;
}

