//v 2021-1-4

input = "C:/Users/joey_/__spyder_projects/MORPHIOUS_GUI/microglia_sample_data/images/treatment/";
output = "C:/Users/joey_/__spyder_projects/MORPHIOUS_GUI/microglia_sample_data/images/image_scales/";


filelist = getFileList(input);

Array.print(filelist);
setBatchMode(true);

for(f=0; f < filelist.length; f++){
		file = filelist[f];
		full_path = input + "/" +file;
		print(file);
		img_name = replace(file, ".tif", "");

		open(full_path);

		getPixelSize(unit, pw, ph, pd);
		scale = round_float(1/pw, 2); //scale = pixel per um

		close();

		scalefile = File.open(output + "/" + img_name + "_scale.txt"); 
		print(scalefile, scale);
		File.close(scalefile);
}
		

setBatchMode(false);


function round_float(number, ndigits){
	x = d2s(number, ndigits);
	y = parseFloat(x);
	return y;
}