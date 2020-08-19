print("this macro maps MORPHIOUS generated cluster coordinates to the original image");
print("the imagedir should be the directory of the initial input images");
print("the clusterdir should be the directory of the MORPHIOUS outputted cluster coordinate files");
print("this macro assumes you may want to map multiple cluster types, therefore requires input of clustertypes, an array of the clustertypes to be mapped");
print("the macro will combine each cluster type as a subdirectory of the outputdir: i.e., [outputdir]/[clustertype]/");
print("the [outputdir]/[clustertype]/ folder should have the following subdirectories: /skeleton_data/");
print("the distal_cluster_reference indicates which cluster should be used in order to identify the distal clusters, the default is combined (i.e., proximal + focal clusters combined)");



imagedir = "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/Iba1_input_7D/";
output_path= "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/output/set1/cluster_files/cluster_imagefiles/150/";
clusterdir= "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/output/set1/cluster_files/cluster_coordinates/single_threshold/150/";

distal_cluster_reference = "combined";
clustertypes = newArray("combined","unclustered","focal","proximal");

//used to map gfap clusters to s100b images
cross_marker_clustering = false;
from="gfap";
to="s100b";
	

batchmode = false;

main(imagedir, output_path, clusterdir, distal_cluster_reference, clustertypes, cross_marker_clustering, from, to, batchmode);


function main(imagedir, output_path, clusterdir, distal_cluster, clustertypes, cross_marker_clustering, from, to, batchmode){
	setBatchMode(batchmode); 
	print("Initiate re-cluster macro V2");
	
	unclustered_cluster_subdir = "unclustered";
	local_threshold=true;

	local_threshold_method = "Phansalkar"; //"Phansalkar"; 
	radius = 60;
	subtract = true; //subtract background
	subtract_by = "100"; // amount to subtract by -- input as string for imageJ to interpret
	despeckle = true; // apply 1 round of despeckling
	contrast = false;
	scale = 1.5;

	cutout_cell_bodies=false;
	
	cross_cell_filename=false;
	from_cell="gfap";
	to_cell="s100b";

	for(c=0;c<clustertypes.length;c++){
		
		cltype = clustertypes[c];

		outputdir = output_path + "/" + cltype +"/skeleton_data/";
		cell_body_dir = output_path + "/" + cltype +"/count_data/rois/";

		full_path = clusterdir+cltype+"/";
		print(full_path);
		
		clusterfiles = getFileList(full_path);
		Array.print(clusterfiles);

		for(j=0;j<clusterfiles.length;j++){
			
			txt_file=clusterfiles[j];
			fname = replace(txt_file,".txt","");

			tif_file=replace(txt_file,"txt","tif");
			//measure focal proximal clusters
			boxes=open_cluster_file(full_path,txt_file);
			print(boxes.length);
			if(boxes.length>0){
				open(imagedir+"/"+tif_file);
				correct_image(subtract,subtract_by,contrast,despeckle);

				if(local_threshold){
					prepare=true;
					add=false;
					window="bin1";
					autolocal_threshold(local_threshold_method, radius, window, add);
				} else {
					set_threshold(set_threshold_path);
				}

				binary_cutout = "bin2";
				run("Duplicate...", "title="+binary_cutout);

				if(cutout_cell_bodies){
					if(cross_cell_filename){
						cell_fname = replace(fname,"gfap","s100b");					
					}
					else{
						cell_fname = fname;
					}
					cell_roi_path = cell_body_dir + "/" + cell_fname+".zip";
					if (File.exists(cell_roi_path)){
						clear_cell_bodies(cell_roi_path);
					}
				}
				
				skeletonize(window);
				skeleton_window = window;
				IF_window="IF_image";
				clear = "Clear Outside";
				cluster_cutout(boxes, skeleton_window, binary_cutout, IF_window, clear);
				
				full_skeleton_analysis(outputdir, fname, skeleton_window, IF_window, binary_cutout);
				reset_all();
			}

			print("completed cluster analysis..");
			
			//measure unclustered clusters
			if(distal_cluster==cltype || unclustered_cluster_subdir == cltype){ //=="combined or proximal"
				unclustered_output = output_path + "/" + unclustered_cluster_subdir +"/skeleton_data/";
				open(imagedir+"/"+tif_file);
				correct_image(subtract,subtract_by,contrast,despeckle);
				print("unclustered clustering..", tif_file);
				
				if(local_threshold){
					prepare=true;
					add=false;
					window="bin1";
					autolocal_threshold(local_threshold_method, radius, window, add);
				} else {
					set_threshold(set_threshold_path);
				}
				binary_cutout = "bin2";
				
				run("Duplicate...", "title="+binary_cutout);
				if(cutout_cell_bodies){
					if(cross_cell_filename){
						cell_fname = replace(fname,"gfap","s100b");					
					}
					else{
						cell_fname = fname;
					}
					cell_body_dir = output_path + "/" + unclustered_cluster_subdir +"/count_data/rois/";
					cell_roi_path = cell_body_dir + "/" + cell_fname+".zip";
					if (File.exists(cell_roi_path)){
						clear_cell_bodies(cell_roi_path);
					}
					
				}
				skeletonize(window);
				skeleton_window = window;
				IF_window="IF_image";	
					
				if(boxes.length>0){
					print("TRUE");
					skeleton_window = window;
					clear = "Clear";
					cluster_cutout(boxes, skeleton_window, binary_cutout, IF_window, clear);
				}
				getStatistics(area, mean);
				print("obtained statistics..");
				print(area, mean);
				
				print("Running skeleton analysis..");
				full_skeleton_analysis(unclustered_output, fname, skeleton_window, IF_window, binary_cutout);
				reset_all();
			}
		}
	}
}


function autolocal_threshold(threshtype, radius, window, add){
	run("Select All");
	run("Duplicate...", "title=bin1");
	run("Duplicate...", "title=IF_image");
	selectWindow("bin1");
	run("8-bit");
	
	if((window == "None") == false){
		selectWindow(window);
	}
	thresh = threshtype;
	run("Auto Local Threshold", "method="+threshtype+" radius="+radius+" parameter_1=0 parameter_2=0 white");

	if(add){
		run("Create Selection");
		roiManager("Add");
	}
}

function prepare_local_threshold(){
	run("Select All");
	run("Duplicate...", "title=bin1");
	run("Duplicate...", "title=IF_image");
	selectWindow("bin1");
	run("8-bit");
}

function skeleton_analysis(){
	print("analyze skeletons");
	run("Analyze Skeleton (2D/3D)", "prune=none show");
	print("completed analysis");
}

function save_data(path,fname){
	selectWindow("Branch information");
	saveAs("Results", path+"/"+fname+"_branchInfo.txt");
	selectWindow("Results");
	saveAs("Results", path+"/"+fname+"_rawInfo.txt");
}

function reset_all(){
	run("Clear Results");
	clear_roi_manager_all();
	close_windows();
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

function clear_roi_manager_all(){
	N = roiManager("count");
	if(N>0){
		roiManager("deselect");
		roiManager("Delete");
	}
	
}

function calculate_percArea(IF_window, binary_cutout){
	selectWindow(IF_window);
	run("Select All");
	getMinAndMax(min, max);
	setThreshold(1, max+1);
	run("Measure");
	back = getResult("Area",0);
	resetThreshold();
	
	selectWindow(binary_cutout);
	run("Select None");
	run("Make Binary");
	run("Create Selection");
	roiManager("Add");

	selectWindow(IF_window);
	roiManager("Select",0);
	run("Measure");

	fore = getResult("Area",1);
	percArea = fore/back;
	print(fore);
	print(back);
	print(percArea);
	run("Clear Results");
	selectWindow("IF_image");
	close();
	return newArray(percArea, fore, back);
}


function full_skeleton_analysis(outputDir, fname, skeleton_window, IF_window, binary_cutout){
	area_metrics = calculate_percArea(IF_window, binary_cutout);
	percArea = area_metrics[0];
	fore = area_metrics[1];
	back = area_metrics[2];

	clear_roi_manager_all();
	selectWindow(skeleton_window);
	run("Select All");
	skeleton_analysis();
	selectWindow("Results");
	setResult("percArea", 0, percArea);
	setResult("Area", 0, fore);
	setResult("backgroundArea", 0, back);
	updateResults();
	save_data(outputDir,fname);
}


function open_cluster_file(dir,clusterfile){
	print(dir+"\\"+clusterfile);
	clusters=File.openAsString(dir+clusterfile);
	boxes=split(clusters,"=");
	return boxes;
}

//open image, subtract background
function open_image(file,subtract){
	open(file);
	if(subtract == "True"){
		run("Subtract Background...", "rolling=100");
	}
}

function make_square(box){
	X = box[0];
	Y = box[1];
	W = box[2];
	H = box[2];
	makeRectangle(X,Y,W,H);
}

function make_clusters(boxes){
	for(k=0;k<boxes.length;k++){
			box=split(boxes[k],"-");
			make_square(box);
			roiManager("Add");
	}
}

function select_roi(n){
	if(n==-1){
		n = roiManager("count")-1;
	}
	roiManager("select", n);
}

function combine_roi(){
	roiManager("deselect");
	roiManager("combine");
	roiManager("add");
	clear_roi_manager(0,1);
}

function clear_roi_manager(start,adjustend){
	print(start);
	array1 = newArray(""+toString(start));
	print(roiManager("count"));
	for (i=1;i<roiManager("count")-adjustend;i++){ 
        array1 = Array.concat(array1,i); 
	} 
	roiManager("select", array1); 
	roiManager("Delete");
}

function skeletonize(window){
	selectWindow(window);
	print("skeletonizing");
	run("Skeletonize (2D/3D)");
}

function cluster_cutout(boxes, skeleton_window, binary_cutout, IF_window, clear){
	make_clusters(boxes);
	combine_roi();

	selectWindow(skeleton_window);
	roiManager("select",0);
	run(clear);
	print("cleared skeleton window");

	selectWindow(binary_cutout);
	roiManager("select",0);
	run(clear);
	print("cleared binary window");

	selectWindow(IF_window);
	roiManager("select",0);
	run(clear);
	print("cleared IF window");

	clear_roi_manager_all();
}


function distal_cluster_cutout_and_skeleton(boxes, skeleton_window, binary_cutout, IF_window, clear){

	if(boxes.length>0){
		make_clusters(boxes);
		combine_roi();

		selectWindow(skeleton_window);
		roiManager("select",0);
		run("Clear");
	
		selectWindow(binary_cutout);
		roiManager("select",0);
		run("Clear");
	
		selectWindow(IF_window);
		roiManager("select",0);
		run("Clear");
		
		run("Select All");
	}
	
	clear_roi_manager_all();
	full_skeleton_analysis(outputDir, fname, skeleton_window, binary_cutout, IF_window);
}

function correct_image(subtract,subtract_by,contrast,despeckle){
	if(contrast == true){
		run("Enhance Contrast...", "saturated="+contrast_by+" normalize");
		print("global contrast");
	} if (indexOf(contrast, "local") >= 0) {
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

function clear_cell_bodies(cell_roi_path){
	selectWindow(window);
	roiManager("Open", cell_roi_path);
	for(i=0; i < roiManager("count"); i++){
		roiManager("select",i);
		run("Clear");
	}
	clear_roi_manager_all();
}

print("... macro completed...");


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
//run("Collect Garbage");
call("java.lang.System.gc");
}
if(collectGarbageShowLogMessage) print("...Collecting Garbage...");
collectGarbageCurrentIndex = 1;
//setBatchMode(true);
}else collectGarbageCurrentIndex++;
}


//eval("script", "System.exit(0);");
