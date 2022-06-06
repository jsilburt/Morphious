//extract immunofluorescence features

//v 2021-1-4

input = "your_path_here/microglia_sample_data/images/treatment/";
output = "your_path_here/microglia_sample_data/features/treatment/intensity/";
logdir = "your_path_here/microglia_sample_data/features/treatment/logs/";

//other parameters 
boxsize=150; // the size of each box in the feature grid. Lower values generates a more granular grid, higher values generates a more sparse grid.

numOffsets=2; //denotes level of overlap.. 2 = 50%, 3 = 66.6% overlap
local_thresh_type = "Phansalkar"; 
radius = 60;

//image preprocessing parameters
subtract_background = true; //subtract background
subtract_by = "50"; // amount to subtract by -- input as string for imageJ to interpret
despeckle = true; // apply 1 round of despeckling
contrast = false; //either local or globally contrast the image
contrast_by = "local_2.0"; //either "local_value", or a float (i.e., "0.3") which is used for global thresholding

batchmode = true; //run in batch mode (i.e., headless mode)



main(input, output, logdir, local_thresh_type, radius, subtract_background, subtract_by, despeckle, contrast, contrast_by, numOffsets, batchmode, boxsize);




function grid_threshold_segment_measure(startX,startY,gridX,gridY,scale,threshtype,radius,apply_threshold){
	x = startX; 
	y = startY;
	picWidth = getWidth();
	picHeight = getHeight();
	tW = gridX;
	tH = gridY;
	//radius=60;
	
	print(tW);
	print(tH);
	
	nX = ( picWidth - x ) / tW;
	nY = ( picHeight - y ) / tH;

	closeWindows = newArray("1","2");
	row = nResults;
	print("===============");
	print(row);
	print("===============");
	
	for(i = 0; i < nY; i++){
		offsetY = y + (i * tH);
		for(j=0;j < nX; j++){
			offsetX = x + (j * tW);

			makeRectangle(offsetX, offsetY, tW, tH);
			run("Duplicate...", "title=1");
			run("Duplicate...", "title=2");
			
			selectWindow("1");
			getStatistics(area,mean);
			print(mean);
			if(mean > 1 ){
				if(apply_threshold){
					threshold(threshtype, radius);
				}
				run("Create Selection");
				roiManager("Add");
				nROI = roiManager("count");
				
				selectWindow("2");
				roiManager("select", nROI-1);
				roiManager("measure");
				
				//delete roi manager
				roiManager("deselect");
				roiManager("delete");

				Table.set("BX", row, offsetX/scale);
				Table.set("BY", row, offsetY/scale);
				row++;
			}
			for(n=0;n<closeWindows.length;n++){
				selectWindow(closeWindows[n]);
				close();
			}
		}
	}
	Table.update;
}

function make_output_directory(outputpath){
	if (!File.exists(outputpath)){
			File.makeDirectory(outputpath);
		}
}


function threshold(threshtype,radius){
	thresh = threshtype;
	run("8-bit");
	run("Auto Local Threshold", "method="+threshtype+" radius="+radius+" parameter_1=0 parameter_2=0 white");
}

function round_float(number, ndigits){
	x = d2s(number, ndigits);
	y = parseFloat(x);
	return y;
}

function correct_image(subtract,subtract_by,despeck,contrast, contrast_by){
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

function clear_roi_manager(){
	array1 = newArray("",toString(0));
	for (i=1;i<roiManager("count");i++){ 
        array1 = Array.concat(array1,i); 
	} 
	roiManager("select", array1); 
	roiManager("Delete");
}

function save_image(output,filename){
	//roiManager("Select", array(1
	filename = replace(filename,".tif","");
	//IJ.renameResults("Summary","Results");
	saveAs("Results", output + filename + ".txt");
}

function reset_(){
	run("Clear Results");
	close();
	collectGarbageIfNecessary();
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


function main(input, output, logdir, local_thresh_type, radius, subtract_background, subtract_by, despeckle, contrast, contrast_by, numOffsets, batch, XY){

	print("BEGIN IMAGEJ MACRO");


	/*
	 * This code deals with opening the relevant files for processing, and retrieving the gridsize from the commandline arugments
	 * 
	 */
	setBatchMode(batch);
	run("Set Measurements...", "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction limit redirect=None decimal=3");
	run("Options...", "iterations=1 count=1 black");
	
	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
	outputdir = "" + year + "-" + (month + 1) + "-" + dayOfMonth + "_" + hour + "h" + minute + "m" + second + "s";
	full_output_path = output + "/" + outputdir + "/";

	make_output_directory(full_output_path);
	
	grid_wise_threshold=true;

	//threshold_whole_image=true;
	
	print(input);
	print(full_output_path);
	
	filelist = getFileList(input);
	Array.print(filelist);
	//stop;
	
	for(i=0; i < filelist.length; i++){
		img = filelist[i];
		fn_len = parseInt(img.length());
		filename = substring(img, 0, (fn_len - 4)); //remove .tif for example
		
		open(input+"/"+img);
		//measurement unit, pixel width, pixel height, pixel density
		getPixelSize(unit, pw, ph, pd);
		scale = round_float(1/pw, 2); //scale = pixel per um
		correct_image(subtract_background,subtract_by,despeckle,contrast, contrast_by);

		for(z=0;z<numOffsets;z++){
			for(j=0;j<numOffsets;j++){
				startX =((parseInt(XY)/numOffsets) * z);
				startY =((parseInt(XY)/numOffsets) * j);

				print(startX);
				print(startY);
				print(filelist.length);
				grid_threshold_segment_measure(startX,startY,XY,XY,scale,local_thresh_type,radius,grid_wise_threshold);
			}
		}
		save_image(full_output_path,filename);
		reset_();
	}

	logfile = File.open(logdir+"/" + outputdir + "_intensity_feature_log.txt"); 
	print(logfile, "output directory\t" + outputdir);
	print(logfile, "local threshold\t" + local_thresh_type);
	print(logfile, "radius\t" + radius);
	print(logfile, "subtract_background\t" + subtract_background);
	print(logfile, "subtract_by\t"	 + subtract_by);
	print(logfile, "despeckle\t" + despeckle);
	print(logfile, "contrast\t" + contrast);
	print(logfile, "contrast_by\t" + contrast_by);
	print(logfile, "input_dir\t" + input);
	print(logfile, "boxsize\t" + XY);
	print(logfile, "numOffsets\t" + numOffsets);
	print(logfile, "image scale\t" + scale);
	File.close(logfile);

	setBatchMode(false);
}







//eval("script", "System.exit(0);");
