# autoXMMepic

READ ME!!!!!!!! 

To run this code from anywhere, you can add an alias to run this code in your ~/.bashrc or ~/.bash_profile file as: alias xmmauto='python /path/to/your/xmmauto.py'

A few things to keep in mind while running the code:

 0. Before running the code,
 
    a) Initialize HEASOFT and, then XMM SAS. 
    
    b) Set your SAS_CCFPATH in your .bashrc or .bash_profile file to the path where your calibration (CCF) files are located. 
    
    c) When you download the ODF files from XMM archive for a given observation, it comes in a zipped file. You should unzip it under a folder named after your /path/to/your/obsID/odf/. There will be another .TAR file which you need to unzip as well. Set your current working directory to the directory where your odf folder resides (for e.g. /path/to/your/obsIDfolder) The code will make an 'analysis' folder in the same directory. 

 1. This code needs to be run in parts, unless you have the source and background region coordinates handy to extract the spectrum, and analyse the region. If you don't have them, which will mostly be the case if you are analysing this data set for the first time, then you should answer 'n' to the latter two questions in this run, and then run the script again when you have the region files ready. 

 2. The region files should be saved in physical coordinates as src_phys.reg, and bkg75_phys.reg in ds9. The physical coordinates are the same for all the 3 EPIC cameras, so you only need 1 file for the source and bkg. Just make sure that the background region is source-free. 

 3. eregionanalyse will give you a 3-sigma upper limit to the count-rate in the source region in 0.3-10 keV images of each detector, and will save the output as *eregaoutput_src.txt.
