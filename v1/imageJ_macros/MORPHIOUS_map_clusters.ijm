print("this macro maps MORPHIOUS generated cluster coordinates to the original image");
print("the imagedir should be the directory of the initial input images");
print("the clusterdir should be the directory of the MORPHIOUS outputted cluster coordinate files");
print("this macro assumes you may want to map multiple cluster types, therefore requires input of clustertypes, an array of the clustertypes to be mapped");
print("the macro will combine each cluster type as a subdirectory of the outputdir: i.e., [outputdir]/[clustertype]/");
print("the [outputdir]/[clustertype]/ folder should have the following subdirectories: /cluster_IF_data/, /cluster_image/, /cutout_image/, /cutout_imaging_no_preprocessing/");
print("the distal_cluster_reference indicates which cluster should be used in order to identify the distal clusters, the default is combined (i.e., proximal + focal clusters combined)");



imagedir = "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/Iba1_input_7D/";;
outputdir= "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/output/set1/cluster_files/cluster_imagefiles/150/";
clusterdir= "G:/lab_files/imageJ_macro_working_directory/Iba1_ML_re/Iba1_iba1-gfap-set_19-11-14/output/set1/cluster_files/cluster_coordinates/single_threshold/150/";

distal_cluster_reference = "combined";
clustertypes = newArray("combined","unclustered","focal","proximal");

//used to map gfap clusters to s100b images
cross_marker_clustering = false;
from="gfap";
to="s100b";
	

batchmode = false;

main(imagedir, outputdir, clusterdir, distal_cluster_reference, clustertypes, cross_marker_clustering, from, to, batchmode);


function main(imagedir, outputdir, clusterdir, distal_cluster, clustertypes, cross_marker_clustering, from, to, batchmode){
	setBatchMode(batchmode); 
	print("Initiate re-cluster macro V2");

	run("Set Measurements...", "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction stack limit redirect=None decimal=3");
	
	_dir = 'G';
		
	cluster_image_subdir = "cluster_image";
	cutout_image_subdir = "cutout_image";
	cluster_data_subdir = "cluster_IF_data";
	raw_cutout_image_subdir = "cutout_image_no_preprocessing";
	untreated_cluster_subdir ="unclustered";
	

	local_threshold=true;

	local_thresh_type = "Phansalkar"; //"Phansalkar"; 
	radius = 60;
	subtract = true; //subtract background
	subtract_by = "100"; // amount to subtract by -- input as string for imageJ to interpret
	despeckle = true; // apply 1 round of despeckling
	contrast = false;
	scale = 1.5;

	//cross marker clustering
	if (cross_marker_clustering){
		raw_cutout_image_subdir = to+"_"+raw_cutout_image_subdir;
	}
	
	print(imagedir);
	print(outputdir);
	print(distal_cluster);

	for(c=0;c<clustertypes.length;c++){
		cltype = clustertypes[c];

		print(cltype);
		full_path = clusterdir+cltype+"/";
		print(full_path);
		
		clusterfiles = getFileList(full_path);
		Array.print(clusterfiles);

		for(j=0;j<clusterfiles.length;j++){
			count = 0;
			txt_file=clusterfiles[j];
			tif_file=replace(txt_file,"txt","tif");
			if(cross_marker_clustering){
				tif_file = cross_stain_cluster_file(tif_file,from,to);
				print(txt_file);
				print(tif_file);
			}
			
			//measure focal proximal clusters
			boxes=open_cluster_file(full_path,txt_file);
			
			if(boxes.length>0){
				if(cross_marker_clustering == false){
					cluster_cutout_and_measure(imagedir,tif_file,txt_file,boxes,
					subtract,subtract_by,contrast,despeckle,
					local_threshold,local_thresh_type,
					outputdir,cltype,cluster_image_subdir,cutout_image_subdir,cluster_data_subdir, radius);
				} 
				cluster_and_cutout_raw_image(imagedir, tif_file, boxes, outputdir, cltype, raw_cutout_image_subdir);
			}
			
			//measure unclustered clusters
			if(distal_cluster==cltype || untreated_cluster_subdir == cltype){ //=="combined or proximal"
				if( cross_marker_clustering == false ){
					distal_cluster_cutout_and_measure(imagedir, tif_file, txt_file,boxes,
						subtract, subtract_by, contrast, despeckle, local_threshold, local_thresh_type,
						untreated_cluster_subdir, cutout_image_subdir, cluster_data_subdir, radius);
				}
				
				raw_distal_cluster_and_cutout(imagedir, tif_file, boxes,
					outputdir, untreated_cluster_subdir, raw_cutout_image_subdir);
			}
			collectGarbageIfNecessary();
			
		}
	}
}

function open_cluster_file(dir,clusterfile){
	print(dir+"\\"+clusterfile);
	clusters=File.openAsString(dir+clusterfile);
	boxes=split(clusters,"=");
	return boxes;
}


function process_image(subtract,subtract_by,contrast,despeckle){
	if(contrast == true){
		run("Enhance Contrast...", "saturated=0.3 normalize");
	}
	if (indexOf(contrast, "local") >= 0) {
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
	selectWindow("1");
	close();
}

function set_threshold(threshpath){
	F=File.openAsString(threshpath);
	getMinAndMax(min,max);
	lower_upper=split(F,"_");
	setThreshold(lower_upper[0],max);
}

function threshold_measure(threshpath,autolocal,selection,radius){
	if(autolocal){
		autolocal_threshold(threshpath,radius);
		selectWindow("2");
		roiManager("select",selection);
		roiManager("measure");
		close();
		
	} else {
		roiManager("select",selection);
		set_threshold(threshpath);
		run("Measure");
	}
}

function background_measure(){
	getMinAndMax(min,max);
	setThreshold(1, max+1);
	run("Measure");
	resetThreshold();
}


function save_image(dir,extra,file){
	print("saving image...");
	saveAs("Tiff",dir+"/"+extra+"/"+file);
	print("image saved...");
}

function save_data(dir,extra,file){
	print("saving data!");
	saveAs("Results", dir+"/"+extra+"/"+file);
	print("data saved");
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

function clear_roi_manager_all(){
	if(roiManager("count") > 0){
		roiManager("deselect");
		roiManager("delete");
	}
}

function reset_all(){
	for(i=0;i<nImages;i++){
		selectImage(i+1);
		close();
	}
	run("Clear Results");
	clear_roi_manager_all();
}

function cross_stain_cluster_file(file, from, to){
	new_file = replace(file,from,to);
	print(new_file);
	return new_file;
}

function cluster_cutout_and_measure(imagedir,tif_file,txt_file,boxes,
	subtract,subtract_by,contrast,despeckle,
	local_threshold,local_thresh_type,
	outputdir,cltype,cluster_image_subdir,cutout_image_subdir,cluster_data_subdir, radius){
	
	open(imagedir+"/"+tif_file);
	roiManager("add");
	process_image(subtract,subtract_by,contrast,despeckle);

	//used to get area of roi
	background_measure();
	
	if(local_threshold){
		threshpath = local_thresh_type;
		selection = 1;
	} else {
		print();
	}
	
	//used to get whole roi fluorsecent measures.
	threshold_measure(threshpath,local_threshold,selection,radius); //

	clear_roi_manager_all();

	//save cluster image
	make_clusters(boxes);
	combine_roi();
	select_roi(-1);
	save_image(outputdir+"/"+cltype,cluster_image_subdir,tif_file);
	clear_roi_manager(0,1);

	//save cluster cutout for analysis
	roiManager("select",0);
	run("Clear Outside");
	background_measure();
		
	threshold_measure(threshpath,local_threshold,selection,radius); //

	save_image(outputdir+"/"+cltype,cutout_image_subdir,tif_file);
	save_data(outputdir+"/"+cltype,cluster_data_subdir,txt_file);
	reset_all();
}


function cluster_and_cutout_raw_image(imagedir, tif_file, boxes, outputdir, cltype, raw_cutout_image_subdir){

	//OUTPUT UNPROCESSED CLUSTER CUTOUTS
	open(imagedir+"/"+tif_file);
	make_clusters(boxes);
	combine_roi();
	select_roi(-1);
	clear_roi_manager(0,1);
	roiManager("select",0);
	run("Clear Outside");
	save_image(outputdir+"/"+cltype,raw_cutout_image_subdir,tif_file);
	reset_all();
}

function distal_cluster_cutout_and_measure(imagedir, tif_file, txt_file,boxes,
	subtract, subtract_by, contrast, despeckle, local_threshold, local_thresh_type,
	untreated_cluster_subdir, cutout_image_subdir, cluster_data_subdir,radius
	){
	
	open(imagedir+"/"+tif_file);
	roiManager("add");
	process_image(subtract,subtract_by,contrast,despeckle);

	clear_roi_manager_all();

	if(boxes.length>0){
		
		make_clusters(boxes);
		combine_roi();
		select_roi(-1);
		run("Clear");
		run("Select All");
		
	} 
	
	if(local_threshold){
		threshpath = local_thresh_type;
		selection = 0;
	} else {
		print();
	}
	
	clear_roi_manager_all();
	background_measure();
	if (getResult("Area", 0) > 0){
		threshold_measure(threshpath,local_threshold,selection,radius); //
		save_image(outputdir+"/"+untreated_cluster_subdir+"/","cutout_image/",tif_file);
		save_data(outputdir+"/"+untreated_cluster_subdir+"/","cluster_IF_data/",txt_file);
	}
	
	reset_all();
}

function raw_distal_cluster_and_cutout(imagedir, tif_file, boxes,
	outputdir, untreated_cluster_subdir, raw_cutout_image_subdir){
	print("DISTAL UNPROCESSED");
	open(imagedir+"/"+tif_file);
	if(boxes.length>0){
		make_clusters(boxes);
		combine_roi();
		clear_roi_manager(0,1);
		select_roi(-1);
		run("Clear");
		print("REST BABY");
	}
	getStatistics(area);
	if( area > 0 ){
		save_image(outputdir+"/"+untreated_cluster_subdir+"/",raw_cutout_image_subdir,tif_file);
	}
	reset_all();
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
//run("Collect Garbage");
call("java.lang.System.gc");
}
if(collectGarbageShowLogMessage) print("...Collecting Garbage...");
collectGarbageCurrentIndex = 1;
//setBatchMode(true);
}else collectGarbageCurrentIndex++;
}


//eval("script", "System.exit(0);");
