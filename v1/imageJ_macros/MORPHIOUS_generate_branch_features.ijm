print("...this macro collects skeleton features from an image...");
print("...input image directory and output directories for the text...");
print("...the predetermined naming structure for image files is: [mouseID]_[treatmentDay]_[treatmentCondition]_[fluorescenseTarget]_[section].tif");




 inputdir = "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/Iba1_input_7D/";
 outputdir = "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/output/set1/feature_files/single_threshold/branch_features/150/";
 logdir = "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/output/set1/logs/";

batchmode = true;

main(inputdir, outputdir, logdir, batchmode, 150);

function main(input_dir, output_dir, logdir, batchmode, xy){
	dir = "G";

	thresh = "Phansalkar";
	numOffsets = 2;
	autothresh = true;
	local_threshold = true;
	radius = 60;
	scale = 1.5; //20x images have a scale of 1.5um per pixel

	background_correct = true;
	subtract = true;
	subtract_by = "100"; //value to subtract bacground by needs to be string to be read by imageJ macro
	contrast = false;
	contrast_by = "0.3";
	despeckle = true;

	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
	
	logfile = File.open(logdir+"/skeletal_branching_log.txt"); 
	print(logfile, "date\t" + year+"/"+month+"/"+dayOfMonth);
	print(logfile, "thresh\t" + thresh);
	print(logfile, "radius\t" + radius);
	print(logfile, "subtract_background\t" + subtract);
	print(logfile, "subtract_by\t"	 + subtract_by);
	print(logfile, "despeckle\t" + despeckle);
	print(logfile, "contrast\t" + contrast);
	print(logfile, "contrast_by\t" + contrast_by);
	print(logfile, "input_dir\t" + input_dir);
	print(logfile, "boxsize\t" + xy);
	print(logfile, "numOffsets\t" + numOffsets);
	File.close(logfile);

	
	setBatchMode(batchmode);

	print(input_dir);
	
	filelist = getFileList(input_dir);
	Array.print(filelist);
	for(i=0; i < filelist.length; i++){
		print(filelist[i]);
		img_file = input_dir + filelist[i];
		open(img_file);
		
		file_inputs= split(filelist[i],"_");
		Array.print(file_inputs);
		
		//pre-determined naming structure for file -- files are named as [mouseID]_[treatmentDay]_[treatmentCondition]_[IFTarget]_[section].txt
		mID=file_inputs[0];
		day=file_inputs[1];
		cond=file_inputs[2];
		cell=file_inputs[3];
		sec = replace(file_inputs[4],".tif","");

		fname = toString(mID)+"_"+toString(day)+"_" + toString(cond) + "_"+toString(cell)+"_"+toString(sec);
		
		for(z=0;z<numOffsets;z++){
			for(j=0;j<numOffsets;j++){
				//defines top X and top Y of first square in grid -- defines how grid array will look
				startX =((parseInt(xy)/numOffsets) * z);
				startY =((parseInt(xy)/numOffsets) * j);
				if(background_correct){
					correct_image(subtract, subtract_by, despeckle, contrast, contrast_by);
				}
				if(autothresh){
					autothreshold(thresh,local_threshold, radius);
				} else {
					threshold(threshold_dir,fname+".txt");
				}
				binarize_skeleton();
				grid_measure_save(output_dir,fname,startX,startY,xy,xy,scale);
			}
		}
		collectGarbageIfNecessary();
	}
	setBatchMode(false);
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
		//setBatchMode(false);
		wait(collectGarbageWaitingTime);
		for(i=0; i<collectGarbageRepetitionAttempts; i++){
			wait(100);
			run("Collect Garbage");
			call("java.lang.System.gc");
		}
		if(collectGarbageShowLogMessage) print("...Collecting Garbage...");
		collectGarbageCurrentIndex = 1;
		//setBatchMode(true);
	} else collectGarbageCurrentIndex++;
}

function correct_image(subtract,subtract_amount,despeck,contrast, contrast_by){
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
		run("Subtract Background...", "rolling="+subtract_amount);
	}
	if(despeck == true){
		run("Despeckle");	
	}
}

function summarize_complexity(){
	print(nResults);
	setOption("ExpandableArrays", true);
	col_features = newArray("# Branches","# Junctions","# End-point voxels","# Junction voxels", "# Slab voxels","Average Branch Length","# Triple points","# Quadruple points", "Maximum Branch Length");
	Array.print(col_features);
	summarized_features = newArray;
	
	for(j=0; j < col_features.length; j++){
		sum = 0;
		for(i=0; i<nResults; i++){
			sum = sum + getResult(col_features[j], i);
		}
		print(col_features[j]);
		print(sum);
		summarized_features[j] = sum;
	}
	summarized_features[col_features.length] = summarized_features[0] * summarized_features[5];
	return summarized_features;
}

print("HERE1");
function grid_measure_save(output, filename, startX, startY, gridX, gridY, scale){
	nBranches = newArray;
	nJunctions = newArray;
	nEnds = newArray;
	nJuncVoxels = newArray;
	nSlab = newArray;
	aveBranch = newArray;
	nTriple = newArray;
	nQuad = newArray;
	maxBranch = newArray;
	totalBranchLength = newArray;
	BX = newArray;
	BY = newArray;
	iters = 0;
	
	x = startX; 
	y = startY;
	picWidth = getWidth();
	picHeight = getHeight();
	tW = gridX;
	tH = gridY;
	nX = ( picWidth - x ) / tW;
	nY = ( picHeight - y ) / tH;
	count = 0;
	//scale = 1.5;
	nextStop=false;
	
	for(i = 0; i < nY; i++){
		offsetY = y + (i * tH);
		for(j=0;j < nX; j++){
			offsetX = x + (j * tW);
			print(offsetX);
			makeRectangle(offsetX, offsetY, tW, tH);
			getStatistics(area, mean);

			if(mean > 0){
				run("Duplicate...", "title=grid");
				selectWindow("grid");
				run("Analyze Skeleton (2D/3D)", "prune=none");
				array1 = summarize_complexity();
				
				Array.print(array1);
				nBranches[iters] = array1[0];
				nJunctions[iters] = array1[1];
				nEnds[iters] = array1[2];
				nJuncVoxels[iters] = array1[3];
				nSlab[iters] = array1[4];
				aveBranch[iters] = array1[5];
				nTriple[iters] = array1[6];
				nQuad[iters] = array1[7];
				maxBranch[iters] = array1[8];
				totalBranchLength[iters] = array1[9];
				BX[iters] = offsetX/scale;
				BY[iters] = offsetY/scale;
				
				selectWindow("Tagged skeleton");
				close();
				selectWindow("grid");
				close();
				run("Clear Results");
				iters++;
				}
			selectWindow(fname+".tif");
			run("Clear Results");
		}
	}
	Array.show("complexity_results",nBranches,nJunctions,nEnds,nJuncVoxels,nSlab,aveBranch,nTriple,nQuad,maxBranch,totalBranchLength,BX,BY);		
	selectWindow("complexity_results");
	saveAs("Results", output+fname+"_"+toString(x)+"-"+toString(y)+".txt");	
	selectWindow(fname+"_"+toString(x)+"-"+toString(y)+".txt");
	run("Close");
}

function autothreshold(threshType,local,radius){
	if(local){
		run("8-bit");
		run("Auto Local Threshold", "method="+threshType+" radius="+radius+" parameter_1=0 parameter_2=0 white");
	}else{
		setAutoThreshold(threshType+" dark no-reset");
	}
}

function threshold(threshdir,file){
	F=File.openAsString(threshdir+"\\"+file);
	getMinAndMax(min,max);
	lower_upper=split(F,"_");
	setThreshold(lower_upper[0],max);
}
	

function binarize_skeleton(){
	run("Make Binary");
	run("Skeletonize (2D/3D)");
}


