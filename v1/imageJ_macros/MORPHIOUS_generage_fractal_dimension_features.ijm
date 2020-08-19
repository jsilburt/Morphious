print("...this macro collects the fractal dimension feature from an image...");
print("...input image directory and output directories for the text file (i.e. output) and for the binarized image (i.e., binary_dir)");
print("...the predetermined naming structure for image files is: [mouseID]_[treatmentDay]_[treatmentCondition]_[fluorescenseTarget]_[section].tif");


input = "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/Iba1_input_7D/";
output = "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/output/set1/feature_files/single_threshold/fractal_dimension/datafiles/150/";
binary_dir = "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/output/set1/feature_files/single_threshold/fractal_dimension/images/";
logdir = "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/output/set1/logs/";
boxsize = 150;
batchmode = true;

main(input, output, binary_dir, logdir, batchmode, boxsize);

function main(input, output, binary_dir, logdir, batchmode, XY){
	setBatchMode(batchmode);

	subtract_background = true; //subtract background
	subtract_by = "100"; // amount to subtract by -- input as string for imageJ to interpret
	despeckle = true; // apply 1 round of despeckling
	ref_treatment = "noFUS"; //only used if pairwise == True, uses ref_treatment section as to assess threshold values and apply to treatment
	exp_treatment = "FUS";
	pairwise = false;
	particles = false;
	contrast = false;
	contrast_by = "0.3";
	scale = 1.5;
	offset=true; //whether add an offset
	numOffsets=2; //denotes level of overlap.. 2 = 50%, 3 = 33.3% overlap

	threshtype = "Phansalkar";
	radius = 60;
	
	print(input);
	print(output);


	logfile = File.open(logdir+"/fractal_dimension_log.txt"); 
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
	print(logfile, "offset\t" + offset);
	File.close(logfile);
	 
	filelist = getFileList(input);
	Array.print(filelist);

	if (offset == true){
		for(i=0; i < filelist.length; i++){
			file_inputs= split(filelist[i],"_");
			txtfile=replace(filelist[i],".tif",".txt");
			filename=replace(filelist[i],".tif","");
			Array.print(file_inputs);
			for(z=0;z<numOffsets;z++){
				for(j=0;j<numOffsets;j++){
					startX =((parseInt(XY)/numOffsets) * z);
					startY =((parseInt(XY)/numOffsets) * j);
					
					process_image(filelist[i],txtfile,input,subtract_background,despeckle,contrast,contrast_by,threshtype,radius);
					set_binary(filelist[i],binary_dir);
					grid_segment(input, output, filename, startX, startY, XY, XY,scale);
				}
			}
		}
	} else {
		print("NOT IMPLEMENTED");
	}
	setBatchMode(false);
}


function grid_segment(input, output, filename, startX, startY, gridX, gridY,scale){
	x = startX; 
	y = startY;
	picWidth = getWidth();
	picHeight = getHeight();
	tW = gridX;
	tH = gridY;
	nX = ( picWidth - x ) / tW;
	nY = ( picHeight - y ) / tH;
	count = 0;
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
	save_image(output,filename,x,y);
	reset_(count);
	print("...reset...");
}

function save_image(output,filename,x,y){
	saveAs("Results", output +filename +"_"+toString(x)+"-"+toString(y)+".txt");
}

/*
function set_threshold(file,threshdir){
	//dir="C:\\Users\\joey\\Documents\\LabWork\\Staining\\immunofluorescense\\Gfap_Iba1_Ki67\\GFAP_Iba1_ki67_batch_output\\Thresholds\\";
	print(threshdir+"\\"+file);
	F=File.openAsString(threshdir+"\\"+file);
	getMinAndMax(min,max);
	lower_upper=split(F,"_");
	setThreshold(lower_upper[0],max);
}
*/

function correct_image(subtract,despeck,contrast, contrast_by){
	if(contrast == true) {
		if (indexOf(contrast_by, "local") >= 0) {
			info = split(contrast_by, "_");
			contrast_by_value = info[1];
			print("local contrast by..",contrast_by_value);
			run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum="+contrast_by_value+" mask=*None* fast_(less_accurate)");
		} else {
			run("Enhance Contrast...", "saturated="+contrast_by+" normalize");
		}
	}
	if(subtract == true){
		run("Subtract Background...", "rolling=50");
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

function reset_(count){
	IJ.deleteRows(0,count+2);
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

function set_binary(file,output){
	saveAs("Tiff",output+file);
	close();
	open(output+file);
}

function process_image(file,txtfile,input,subtract_background,despeckle,contrast,contrast_by, threshtype, radius){
	print(input+file);
	open(input+file);
	correct_image(subtract_background,despeckle,contrast,contrast_by);
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
		print("COLLECTING LOTS OF MOTHA FUCKIN GARBAGE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
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
