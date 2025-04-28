# ----------------------------
# Import Libraries
# ----------------------------
import os
import sys
import glob
import time

time_stamp = time.time()

# Terminal color codes for user prompts
CGREEN = '\033[92m'		# Green
CRED = '\033[91m' 		# Red
CYELL = '\033[33m'		# Yellow
CPURPLE = '\033[95m'	# Purple
CEND = '\033[0m'		# Reset


# ----------------------------
# Initial Instructions
# ----------------------------
print(CGREEN + '''
READ ME!!!

A few things to keep in mind while running the code:

0. Before running the code,
	a) Set your SAS_CCFPATH in your .bashrc or .bash_profile file to the path where your calibration (CCF) files are located.
   	b) Move all your unzipped odf files (downloaded from XMM archive) into a folder named 'odf' in your preferred directory (e.g., /path/to/your/xmm_obsID/).
   	c) Set your current working directory to /path/to/your/xmm_obsID/ and run the code. The code will make your analysis folder in the parent directory of the odf folder. 
   	d) Initialize HEASOFT and then XMM SAS. Run the code from /path/to/your/preferred/directory.
   
1. This code needs to be run in parts, unless you have the source and background region coordinates handy to extract the spectrum and analyze the region. 
If you don't have them (e.g., for when you're analyzing this dataset for the first time), answer 'n' to the latter two questions in this run.

2. The region files should be saved in physical coordinates as src_phys.reg and bkg75_phys.reg in ds9. 
The physical coordinates are the same for all 3 EPIC cameras, so you only need 1 file for the source and background. Ensure the background region is source-free.
''' + CEND)




def check_sas():
	"""Check if XMM SAS software is initialized"""
	
	if not os.environ.get('SAS_DIR'):
		print(CRED + 'ERROR: XMM SAS is not initialized!' + CEND)
		sys.exit(1)



def safe_glob(pattern):
    """Safe wrapper for glob with error handling"""
    
    try:
        results = glob.glob(pattern)
        return results
    
    except Exception as e:
        print(CRED + f"Fatal Error: {str(e)}" + CEND)
        sys.exit(1)


def sas_setup(firsttime,initodfdir):
	"""Initial setup to analyze the EPIC camera data"""

	if firsttime == 'y':
		initdir = os.path.join(initodfdir,'odf')
		os.environ['SAS_ODF'] = initdir					# Set the initial SAS_ODF environment

		try:
			os.makedirs(foldname,exist_ok=False)			# Make the analysis directory
		except:
			None

		workdir = os.path.join(initodfdir,foldname)
		os.chdir(workdir)
		os.system(f"cifbuild > output_log_{time_stamp}.txt")							# Run cifbuild to generate the Calibration Index File
		ccfpath = os.path.join(workdir,"ccf.cif")	
		os.environ['SAS_CCF'] = ccfpath					# Set the SAS_CCF environment
		os.system(f"odfingest >> output_log_{time_stamp}.txt")							# Run odfingest to produce summary files
	
	if firsttime == 'n':
		workdir = os.path.join(initodfdir,foldname)
		if os.path.exists(workdir):
			os.environ['SAS_ODF'] = workdir
			os.chdir(workdir)
			ccfpath = os.path.join(workdir,"ccf.cif")
			os.environ['SAS_CCF'] = ccfpath
		else:
			print (CRED + 'Analysis folder does not exist. Set one and re-run the code.' + CEND)
			sys.exit(1)
	
	sumsaspath = safe_glob('./*SUM.SAS')[0]
	os.environ['SAS_ODF'] = sumsaspath					# Set SAS_ODF environment with the revised path
	
	print (CYELL + "Initial SAS setup complete" + CEND)



def analysis(cams_to_process):
	"""Processes EPIC-MOS and EPIC-PN data: event lists, filtering, imaging."""

	if cams_to_process == 'all':
		cams_to_process = ['m1','m2','pn']

	print (CYELL + f"Cameras to process: {cams_to_process}" + CEND)
	
	for cam in cams_to_process:
		print (CYELL + f"Processing {cam} data..." + CEND)
		
		if cam in ['m1','m2']:
            # MOS-specific processing

			os.system(f"emproc >> output_log_{time_stamp}.txt")

			if cam == 'm1':
				m1 = safe_glob('*EMOS1_*_ImagingEvts.ds')[0].split('/')[0]			# Search for the main MOS1 output file from emproc
				os.rename(m1,'m1.fits')
			
			if cam == 'm2':
				m2 = safe_glob('*EMOS2_*_ImagingEvts.ds')[0].split('/')[0]			# Search for the main MOS2 output file from emproc
				os.rename(m2,'m2.fits')

			
			expr_string = '#XMMEA_EM && (PI>10000) && (PATTERN==0)'
			rate_expr = 'RATE<=0.35'
			gti_expr = f'#XMMEA_EM && gti({cam}_gti.fits,TIME) && (PI>150)'
			bin_val = 20


		if cam == 'pn':
			# PN-specific processing

			os.system(f"epchain >> output_log_{time_stamp}.txt")
			#epn = glob.glob('*EPN_*_ImagingEvts.ds')[0].split('/')[0] 			# Search for the main PN output file from epchain
			
			epn = safe_glob('*PN*PIEVLI*.FIT')[0].split('/')[0] 				# Search for the main PN output file from epchain
			os.rename(epn,'pn.fits')

			expr_string = '#XMMEA_EP && (PI>10000&&PI<12000) && (PATTERN==0)'
			rate_expr = 'RATE<=0.4'
			gti_expr = f'#XMMEA_EP && gti({cam}_gti.fits,TIME) && (PI>150)'
			bin_val = 80
			
			
		# Create a light-curve above 10 keV to check for flaring high background period
		os.system(
					f"evselect table={cam}.fits withrateset=Y rateset={cam}_hfl_lc.fits " 
					f"maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='{expr_string}' >> output_log_{time_stamp}.txt"
					)
		
		# Create a good time interval (GTI) file filtering out the high background periods
		os.system(
					f"tabgtigen table={cam}_hfl_lc.fits expression='{rate_expr}' gtiset={cam}_gti.fits >> output_log_{time_stamp}.txt"
				 )
		
		# Create an event list which is free of high background periods. Also restrict to well calibrated patterns and energy band
		os.system(
					f"evselect table={cam}.fits withfilteredset=Y filteredset={cam}_clean.fits destruct=Y " 
					f"keepfilteroutput=T expression='{gti_expr}' >> output_log_{time_stamp}.txt"
				 )
		
		# Create an fits image of the above cleaned event file
		os.system(
					f"evselect table={cam}_clean.fits imagebinning=binSize imageset={cam}_image_all.fits " 
					f"withimageset=yes xcolumn=X ycolumn=Y ximagebinsize={bin_val} yimagebinsize={bin_val} >> output_log_{time_stamp}.txt"
				 )
			
	print (CYELL + "All processing completed successfully!" + CEND)


def make_spec(cams_to_process, specprefix):
	"""Make EPIC-MOS and EPIC-PN spectral files"""

	if cams_to_process == 'all':
		cams_to_process = ['m1','m2','pn']

	print (CYELL + f"Cameras to process for spectral analysis: {cams_to_process}" + CEND)

	# Read the source region file. Same for all EPIC cameras
	srcregfile = glob.glob('src_phys.reg')[0]
	with open(srcregfile,'r') as f:
		for line in f:
			pass
		last_line = line
	srcreg = last_line

	# Read the background region file. Same for all EPIC cameras
	bkgregfile = glob.glob('bkg75_phys.reg')[0]
	with open(bkgregfile,'r') as f:
		for line in f:
			pass
		last_line = line
	bkgreg = last_line
	
	for cam in cams_to_process:
		print (CYELL + f"Processing {cam} data..." + CEND)

		if cam in ['m1','m2']:
			src_expr_string = f'#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN {srcreg})'
			bkg_expr_string = f'#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN {bkgreg})'
			specchanmax = 11999
		
		if cam == 'pn':
			src_expr_string = f'(FLAG==0) && (PATTERN<=4) && ((X,Y) IN {srcreg})'
			bkg_expr_string = f'(FLAG==0) && (PATTERN<=4) && ((X,Y) IN {bkgreg})'
			specchanmax = 20479
		

		# Create source spectrum for EPIC cam with specprefix in the name of the files.
		os.system(
					f"evselect table={cam}_clean.fits withspectrumset=yes spectrumset={cam}_{specprefix}_spectrum.fits energycolumn=PI spectralbinsize=1 " 
					f"withspecranges=yes specchannelmin=0 specchannelmax={specchanmax} expression='{src_expr_string}' >> output_log_{time_stamp}.txt"
				 )

		# Create background spectrum for EPIC cam with specprefix in the name of the files.
		os.system(
					f"evselect table={cam}_clean.fits withspectrumset=yes spectrumset={cam}_{specprefix}_bkg_spectrum.fits energycolumn=PI spectralbinsize=1 "
					f"withspecranges=yes specchannelmin=0 specchannelmax={specchanmax} expression='{bkg_expr_string}' >> output_log_{time_stamp}.txt"
				 )
		
		#  Calculate and write the BACKSCAL keyword in respective EPIC spectra. Accounts for bad pixels and ccd gaps.
		os.system(
					f"backscale spectrumset={cam}_{specprefix}_spectrum.fits withbadpixcorr=True badpixlocation={cam}_clean.fits >> output_log_{time_stamp}.txt;"
					f"backscale spectrumset={cam}_{specprefix}_bkg_spectrum.fits withbadpixcorr=True badpixlocation={cam}_clean.fits >> output_log_{time_stamp}.txt"
				 )

		# Create redistribution matrix file (RMF) for a given spectrum.
		os.system(
					f"rmfgen spectrumset={cam}_{specprefix}_spectrum.fits rmfset={cam}_{specprefix}.rmf >> output_log_{time_stamp}.txt"
				 )
		
		# Create Ancillary Response File (ARF) for the source.
		os.system(
					f"arfgen spectrumset={cam}_{specprefix}_spectrum.fits arfset={cam}_{specprefix}.arf withrmfset=yes "
					f"rmfset={cam}_{specprefix}.rmf badpixlocation={cam}_clean.fits detmaptype=psf >> output_log_{time_stamp}.txt"
				)
		
		# Group the spectral files for each cam
		os.system(
					f"specgroup spectrumset={cam}_{specprefix}_spectrum.fits mincounts=1 oversample=3 rmfset={cam}_{specprefix}.rmf " 
					f"arfset={cam}_{specprefix}.arf backgndset={cam}_{specprefix}_bkg_spectrum.fits groupedset={cam}_{specprefix}_grp.fits >> output_log_{time_stamp}.txt"
				)


def make_images(cams_to_process,lowband,highband,bandname):
	"""Make images restricted to specific energy range"""
    
	if cams_to_process == 'all':
		cams_to_process = ['m1','m2','pn']
	
	
	lowband = [int(x) for x in lowband.split(',')]
	highband = [int(x) for x in highband.split(',')]
	bandname = [x for x in bandname.split(',')]
	

	for i in range(len(lowband)):
		for cam in cams_to_process:

			if cam in ['m1','m2']:
				expr_string = f'(FLAG==0) && (PATTERN<=12) && (PI>{lowband[i]}&&PI<{highband[i]})'
				bin_val = 20
			
			if cam == 'pn':
				expr_string = f'(FLAG==0) && (PATTERN<=4) && (PI>{lowband[i]}&&PI<{highband[i]})'
				bin_val = 80
			
			
			print (CYELL + f"Making images of {cam} data..." + CEND)

			os.system(
						f"evselect table={cam}_clean.fits imagebinning=binSize imageset={cam}_image_{bandname[i]}.fits withimageset=yes " 
						f"xcolumn=X ycolumn=Y ximagebinsize={bin_val} yimagebinsize={bin_val} expression='{expr_string}' >> output_log_{time_stamp}.txt"
					 )



if __name__ == "__main__":

	
	check_sas()						# Check if XMM SAS software is initialized

	# ----------------------------
	# User Inputs
	# ----------------------------
	firsttime = input(CPURPLE + "Is this the first time this observation is being analysed?(y or n). If you only want setup, type n (for re-runs):" + CEND).strip()
	inp_cams = input(CPURPLE + "Enter EPIC cameras to process from m1, m2, pn (comma-separated, or 'all' for all cameras):" + CEND).strip().lower()
	foldname = input(CPURPLE + "Analysis folder name? " + CEND).strip()
	makeimg = input(CPURPLE + "Do you want to make images in different bands? (y or n)" + CEND).strip()
	makespec = input(CPURPLE + "Do you want to extract the spectrum? (y or n)" + CEND).strip()
	
	initodfdir = os.path.abspath(os.getcwd())	

	sas_setup(firsttime,initodfdir)

	selected_cams = [cam.strip() for cam in inp_cams.split(',')]

	if firsttime == 'y':
		analysis(selected_cams)

	if makeimg == 'y':
		lowband = input(CYELL+'Enter the lower end of the bands (e.g. enter 200 for 0.2keV or 2000 for 2keV) separated by commas for multiple images: '+CEND)
		highband = input(CYELL+'Enter the higher end of the bands (e.g. enter 200 for 0.2keV or 2000 for 2keV) separated by commas for multiple images:'+CEND)
		bandname = input(CYELL+'Enter suffixes for image names (e.g. X_Y for m1_image_X_Y.fits) separated by commas: '+CEND)
		
		make_images(selected_cams,lowband,highband,bandname)
	
	if makespec == 'y':
		specprefix = input(CYELL+'Prefix for naming spectral files: '+CEND)
		make_spec(selected_cams, specprefix)

	


	
	
	

	

	
		

	
	
	
	
