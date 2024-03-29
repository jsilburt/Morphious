
//extract fractal dimension features

//v 2021-1-4

input = "your_path_here/microglia_sample_data/images/treatment/";
output = "your_path_here/microglia_sample_data/features/treatment/fractal/";
binary_dir = "your_path_here/microglia_sample_data/features/treatment/binarized_images/";
logdir = "your_path_here/microglia_sample_data/features/treatment/logs/";

//grid and threshold parameters
boxsize = 150;
numOffsets=2; //denotes level of overlap.. 2 = 50%, 3 = 33.3% overlap
threshtype = "Phansalkar";
radius = 60;

//image preprocessing parameters
subtract_background = true; //subtract background
subtract_by = "50"; // amount to subtract by -- input as string for imageJ to interpret
despeckle = true; // apply 1 round of despeckling
contrast = false;
contrast_by = "0.3"; //either "local_value", or a float (i.e., "0.3") which is used for global thresholding

batchmode = true;
main(input, output, binary_dir, logdir, batchmode, boxsize, subtract_background, subtract_by, despeckle, contrast, contrast_by, boxsize, numOffsets, threshtype, radius);

function main(input, output, binary_dir, logdir, batchmode, XY, subtract_background, subtract_by, despeckle, contrast, contrast_by, boxsize, numOffsets, threshtype, radius){
	setBatchMode(batchmode);
	run("Options...", "iterations=1 count=1 black");
	
	print(input);
	print(output);

	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
	outputdir = "" + year + "-" + (month + 1) + "-" + dayOfMonth + "_" + hour + "h" + minute + "m" + second + "s";
	full_output_path = output + "/" + outputdir + "/";

	make_output_directory(full_output_path);
	 
	filelist = getFileList(input);
	Array.print(filelist);

	for(i=0; i < filelist.length; i++){
		f = filelist[i];
		fn_len = parseInt(f.length());
		filename = substring(f, 0, (fn_len - 4)); //remove .tif for example
		txtfile = filename + ".txt";

		process_image(f,txtfile,input,subtract_background, subtract_by, despeckle,contrast,contrast_by,threshtype,radius);
		getPixelSize(unit, pw, ph, pd);
		scale = round_float(1/pw, 2); //scale = pixel per um
		save_binary(filelist[i],binary_dir);
		count=0;
		for(z=0;z<numOffsets;z++){
			for(j=0;j<numOffsets;j++){
				startX =((parseInt(XY)/numOffsets) * z);
				startY =((parseInt(XY)/numOffsets) * j);
				count = grid_segment(startX, startY, XY, XY, scale, count);
			}
		}
		save_image(full_output_path,filename);
		reset_();
		print("...reset...");
	}
	
	logfile = File.open(logdir+"/" + outputdir + "_fractal_dimension_log.txt"); 
	print(logfile, "threshtype\t" + threshtype);
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

function make_output_directory(outputpath){
	if (!File.exists(outputpath)){
			File.makeDirectory(outputpath);
		}
}

function round_float(number, ndigits){
	x = d2s(number, ndigits);
	y = parseFloat(x);
	return y;
}

function grid_segment(startX, startY, gridX, gridY,scale, count){
	x = startX; 
	y = startY;
	picWidth = getWidth();
	picHeight = getHeight();
	tW = gridX;
	tH = gridY;
	nX = ( picWidth - x ) / tW;
	nY = ( picHeight - y ) / tH;
	for(i = 0; i < nY; i++){
		offsetY = y + (i * tH);
		for(j=0;j < nX; j++){
			offsetX = x + (j * tW);
			makeRectangle(offsetX, offsetY, tW, tH);
			roiManager("Add");
			frac_check = check_if_fractal();
			if(frac_check){
				fractal_box();
				Table.set("BX", count, offsetX/scale);
				Table.set("BY", count, offsetY/scale);
				Table.update;
				count++;
			}
			roiManager("Delete");
		}
	}
	return count;
}

function save_image(output,filename){
	saveAs("Results", output +"/"+ filename + ".txt");
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

function threshold_binary_from_file(file,threshdir){
	set_threshold(file,threshdir);
	setOption("BlackBackground", true);
	run("Make Binary");
}

function local_threshold(threshtype,radius){
	run("8-bit");
	run("Auto Local Threshold", "method="+threshtype+" radius="+radius+" parameter_1=0 parameter_2=0 white");
}

function reset_(){
	//IJ.deleteRows(0,count+2);
	run("Clear Results");
	close();
	collectGarbageIfNecessary();
}

function fractal_box(){
	run("Clear Outside");
	roiManager("Select", 0);
	run("Crop");
	run("Fractal Box Count...", "box=2,3,4,6,8,12,16,32,64 black");
	close();
	run("Revert");
}

function save_binary(file,output){
	saveAs("Tiff",output+file);
	close();
	open(output+file);
}

function process_image(file,txtfile,input,subtract_background, subtract_by, despeckle,contrast,contrast_by, threshtype, radius){
	print(input+"/"+file);
	open(input+"/"+file);
	correct_image(subtract_background,subtract_by, despeckle,contrast,contrast_by);
	local_threshold(threshtype, radius);
}

function check_if_fractal(){
	result = false;
	getStatistics(area, mean);
	if(mean > 0.1){
		result=true;
	}
	return result;
}


//Global variables
var collectGarbageInterval = 2; // the garbage is collected after n Images
var collectGarbageCurrentIndex = 1; // increment variable for garbage collection
var collectGarbageWaitingTime = 100; // waiting time in milliseconds before garbage is collected
var collectGarbageRepetitionAttempts = 3; // repeats the garbage collection n times
var collectGarbageShowLogMessage = true; // defines whether or not a log entry will be made


//-------------------------------------------------------------------------------------------
// this function collects garbage after a certain interval
//-------------------------------------------------------------------------------------------
function collectGarbageIfNecessary(){
	if(collectGarbageCurrentIndex == collectGarbageInterval){
		setBatchMode(false);
		wait(collectGarbageWaitingTime);
		for(i=0; i<collectGarbageRepetitionAttempts; i++){
			wait(100);
			run("Collect Garbage");
			
			call("java.lang.System.gc");
			}
		if(collectGarbageShowLogMessage){
			print("...Collecting Garbage...");
		}
		collectGarbageCurrentIndex = 1;
		setBatchMode(true);
		}else {
			collectGarbageCurrentIndex++;
		}
}
