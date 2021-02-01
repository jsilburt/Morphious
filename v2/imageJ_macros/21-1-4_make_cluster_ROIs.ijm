



batchmode = false;
imagedir = "C:/Users/joey_/__spyder_projects/MORPHIOUS_GUI/microglia_sample_data/images/treatment/";
clusterdir= "C:/Users/joey_/__spyder_projects/MORPHIOUS_GUI/microglia_sample_data/output/cluster_coords/test_dataset/06-01-2021_14h26m44s/";
outputpath = "C:/Users/joey_/__spyder_projects/MORPHIOUS_GUI/microglia_sample_data/output/cluster_rois/test_dataset/";
clusters = newArray("focal", "proximal", "combined");

main(batchmode, imagedir, clusterdir, outputpath, clusters);

function main(batchmode, imagedir, clusterdir, outputpath, clusters){
	setBatchMode(batchmode); 
	
	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
	outputdir = "" + dayOfMonth + "-" + (month + 1) + year + "-" + "_" + hour + "h" + minute + "m" + second + "s";
	print(outputdir);

	full_output_path = outputpath + "/" + outputdir;

	if (!File.exists(full_output_path)){
			File.makeDirectory(full_output_path);
		}

	
	for(i=0; i<clusters.length; i++){
		cl = clusters[i];
		full_path = clusterdir + cl+ "/";
		files = getFileList(full_path);
		full_output_path = outputpath + "/" + outputdir + "/" + cl + "/";
		if (!File.exists(full_output_path)){
			File.makeDirectory(full_output_path);
		}
		
		for(ii=0; ii<files.length; ii++){
			file = files[ii];
			fname = replace(file,".csv", "");
			img = replace(file, ".csv", ".tif");
			open(imagedir+"/"+img);
			make_clusters(full_path+"/"+file);
			combine_roi();
			nroi = roiManager("count");
			roiManager("select", nroi-1);
			roiManager("save selected", full_output_path+"/"+fname+".roi");
			reset_all();
		}
	}
}


function clear_roi_manager(start,adjustend){
	print(start);
	print(roiManager("count"));
	while(roiManager("count")>adjustend){
		roiManager("select",start);
        roiManager("Delete");
	}
}

function clear_roi_manager_all(){
	if(roiManager("count") > 0){
		roiManager("deselect");
		roiManager("delete");
	}
}

function combine_roi(){
	roiManager("deselect");
	roiManager("combine");
	roiManager("add");
}

function make_square(bx, by, size){
	X = bx;
	Y = by;
	W = size;
	H = size;
	makeRectangle(X,Y,W,H);
}

function make_clusters(path){
	//"C:/Users/joey_/__spyder_projects/MORPHIOUS_GUI/sample_data/output/test_dataset/05-01-2021_12h38m49s/focal/JS1_FUS_sec4.csv"
	run("Results... ", "open="+path);
	for(i=0; i<nResults; i++){
		bx = getResult("BX", i);
		by = getResult("BY", i);
		size = getResult("Boxsize", i);
		print(bx, by, size);
		make_square(bx, by, size);
		roiManager("Add");
	}
}

function reset_all(){
	run("Clear Results");
	close_windows();
	clear_roi_manager_all();
	collectGarbageIfNecessary();
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


//Global variables
var collectGarbageInterval = 2; // the garbage is collected after n Images
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
}else collectGarbageCurrentIndex++;
}

