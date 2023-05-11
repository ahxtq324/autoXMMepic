###

import subprocess
import os
import glob
import numpy as np

CRED = '\033[91m'
CYELL = '\033[33m'
CEND = '\033[0m'

print (CRED+'READ ME!!!!!!!! \n\n A few things to keep in mind while running the code:\n\n 0. Before running the code,\n a) Initialize HEASOFT and, then XMM SAS. \n b) Set your SAS_CCFPATH in your .bashrc or .bash_profile file to the path where your calibration (CCF) files are located. \n c) move all your unzipped odf files into a folder named \'odf\', and set your current working directory to the directory where your odf folder resides The code will make an \'analysis\' folder in the same directory. \n\n 1. This code needs to be run in parts, unless you have the source and background region coordinates handy to extract the spectrum, and analyse the region. If you don\'t have them, which will mostly be the case if you are analysing this data set for the first time, then you should answer \'n\' to the latter two questions in this run, and then run the script again when you have the region files ready. \n\n 2.The region files should be saved in physical coordinates as src_phys.reg, and bkg75_phys.reg in ds9. The physical coordinates are the same for all the 3 EPIC cameras, so you only need 1 file for the source and bkg. Just make sure that the background region is source-free. \n\n 3. eregionanalyse will give you a 3-sigma upper limit to the count-rate in the source region in 0.3-10 keV images of each detector, and will save the output as *eregaoutput_src.txt.\n\n'+CEND)

firsttime = input(CYELL+'Is this the first time this observation is being analysed?(y or n). If you only want setup, type n (for re-runs):'+CEND)

makeimg = input(CYELL+'Do you want to make images in different bands? (y or n)'+CEND)
    
makespec = input(CYELL+'Do you want to extract the spectrum? (y or n)'+CEND)
    
reganalyse = input(CYELL+'Do you want to the analyze the region? (y or n)'+CEND)
    



initodfdir = os.path.abspath(os.getcwd())

def sas_setup(firsttime,initodfdir):
	foldname = 'analysis2'
	if firsttime == 'y':
		os.mkdir('%s'%foldname)
		initdir = os.path.join(initodfdir,'odf')
		os.environ['SAS_ODF']= initdir
		workdir = os.path.join(initodfdir,"%s"%foldname)
		os.chdir(workdir)
		os.system('cifbuild')
		ccfpath = os.path.join(workdir,"ccf.cif")
		os.environ['SAS_CCF']=ccfpath
		os.system("odfingest")
	if firsttime == 'n':
		workdir = os.path.join(initodfdir,"%s"%foldname)
		os.environ['SAS_ODF']=initodfdir
		os.chdir(workdir)
		ccfpath = os.path.join(workdir,"ccf.cif")
		os.environ['SAS_CCF']=ccfpath
	sumsaspath = glob.glob('./*SUM.SAS')[0]
	os.environ['SAS_ODF']=sumsaspath
	
def emos_analysis():
	os.system('emproc')
	m1 = glob.glob('*EMOS1_*_ImagingEvts.ds')[0].split('/')[0]
	m2 = glob.glob('*EMOS2_*_ImagingEvts.ds')[0].split('/')[0]
	os.rename(m1,'m1.fits')
	os.rename(m2,'m2.fits')

	os.system("evselect table=m1.fits withrateset=Y rateset=m1_hfl_lc.fits maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='#XMMEA_EM && (PI>10000) && (PATTERN==0)'")
	os.system("evselect table=m2.fits withrateset=Y rateset=m2_hfl_lc.fits maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='#XMMEA_EM && (PI>10000) && (PATTERN==0)'")
	
	os.system("tabgtigen table=m1_hfl_lc.fits expression='RATE<=0.35' gtiset=m1_gti.fits")
	os.system("tabgtigen table=m2_hfl_lc.fits expression='RATE<=0.35' gtiset=m2_gti.fits")

	os.system("evselect table=m1.fits withfilteredset=Y filteredset=m1_clean.fits destruct=Y keepfilteroutput=T expression='#XMMEA_EM && gti(m1_gti.fits,TIME) && (PI>150)'")
	os.system("evselect table=m2.fits withfilteredset=Y filteredset=m2_clean.fits destruct=Y keepfilteroutput=T expression='#XMMEA_EM && gti(m2_gti.fits,TIME) && (PI>150)'")
	

	os.system("evselect table=m1_clean.fits imagebinning=binSize imageset=m1_image_all.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=20 yimagebinsize=20")
	os.system("evselect table=m2_clean.fits imagebinning=binSize imageset=m2_image_all.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=20 yimagebinsize=20")

		
def emos_spec(specprefix):
	m1srcregfile = glob.glob('src_phys.reg')[0]
	with open(m1srcregfile,'r') as f:
		for line in f:
			pass
		last_line = line
	m1srcreg = last_line
	
	m1bkgregfile = glob.glob('bkg75_phys.reg')[0]
	with open(m1bkgregfile,'r') as f:
		for line in f:
			pass
		last_line = line
	m1bkgreg = last_line

	m2srcregfile = glob.glob('src_phys.reg')[0]
	with open(m2srcregfile,'r') as f:
		for line in f:
			pass
		last_line = line
	m2srcreg = last_line

	m2bkgregfile = glob.glob('bkg75_phys.reg')[0]
	with open(m2bkgregfile,'r') as f:
		for line in f:
			pass
		last_line = line
	m2bkgreg = last_line


	os.system("evselect table=m1_clean.fits withspectrumset=yes spectrumset=m1_%s_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 expression='#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN %s)'"%(specprefix,m1srcreg))
	os.system("evselect table=m2_clean.fits withspectrumset=yes spectrumset=m2_%s_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 expression='#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN %s)'"%(specprefix,m2srcreg))

	os.system("evselect table=m1_clean.fits withspectrumset=yes spectrumset=m1_%s_bkg_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 expression='#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN %s)'"%(specprefix,m1bkgreg))
	os.system("evselect table=m2_clean.fits withspectrumset=yes spectrumset=m2_%s_bkg_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 expression='#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN %s)'"%(specprefix,m2bkgreg))
	
	os.system("backscale spectrumset=m1_%s_spectrum.fits badpixlocation=m1_clean.fits;backscale spectrumset=m1_%s_bkg_spectrum.fits badpixlocation=m1_clean.fits"%(specprefix,specprefix))
	os.system("backscale spectrumset=m2_%s_spectrum.fits badpixlocation=m2_clean.fits;backscale spectrumset=m2_%s_bkg_spectrum.fits badpixlocation=m2_clean.fits"%(specprefix,specprefix))

	
	os.system("rmfgen spectrumset=m1_%s_spectrum.fits rmfset=m1_%s.rmf"%(specprefix,specprefix))
	os.system("rmfgen spectrumset=m2_%s_spectrum.fits rmfset=m2_%s.rmf"%(specprefix,specprefix))

	os.system("arfgen spectrumset=m1_%s_spectrum.fits arfset=m1_%s.arf withrmfset=yes rmfset=m1_%s.rmf badpixlocation=m1_clean.fits detmaptype=psf"%(specprefix,specprefix,specprefix))
	os.system("arfgen spectrumset=m2_%s_spectrum.fits arfset=m2_%s.arf withrmfset=yes rmfset=m2_%s.rmf badpixlocation=m2_clean.fits detmaptype=psf"%(specprefix,specprefix,specprefix))

	os.system("specgroup spectrumset=m1_%s_spectrum.fits mincounts=1 oversample=3 rmfset=m1_%s.rmf arfset=m1_%s.arf backgndset=m1_%s_bkg_spectrum.fits groupedset=m1_%s_grp.fits"%(specprefix,specprefix,specprefix,specprefix,specprefix))
	os.system("specgroup spectrumset=m2_%s_spectrum.fits mincounts=1 oversample=3 rmfset=m2_%s.rmf arfset=m2_%s.arf backgndset=m2_%s_bkg_spectrum.fits groupedset=m2_%s_grp.fits"%(specprefix,specprefix,specprefix,specprefix,specprefix))
	

def epn_analysis():
    print ('Now processing EPN files...')
    os.system('epchain')
    #epn = glob.glob('*EPN_*_ImagingEvts.ds')[0].split('/')[0] ### for epproc
    epn = glob.glob('*PN*PIEVLI*.FIT')[0].split('/')[0] ### for epchain
    os.rename(epn,'pn.fits')

    os.system("evselect table=pn.fits withrateset=Y rateset=pn_hfl_lc.fits maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='#XMMEA_EP && (PI>10000&&PI<12000) && (PATTERN==0)'")

    os.system("tabgtigen table=pn_hfl_lc.fits expression='RATE<=0.4' gtiset=pn_gti.fits")


    os.system("evselect table=pn.fits withfilteredset=Y filteredset=pn_clean.fits destruct=Y keepfilteroutput=T expression='#XMMEA_EP && gti(pn_gti.fits,TIME) && (PI>150)'")

    os.system("evselect table=pn_clean.fits imagebinning=binSize imageset=pn_image_all.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80")
	
		
def epn_spec(specprefix):
	pnsrcregfile = glob.glob('src_phys.reg')[0]
	with open(pnsrcregfile,'r') as f:
		for line in f:
			pass
		last_line = line
	pnsrcreg = last_line
	print (pnsrcreg)
	
	pnbkgregfile = glob.glob('bkg75_phys.reg')[0]
	with open(pnbkgregfile,'r') as f:
		for line in f:
			pass
		last_line = line
	pnbkgreg = last_line	
	
	
	os.system("evselect table=pn_clean.fits withspectrumset=yes spectrumset=pn_%s_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 expression='(FLAG==0) && (PATTERN<=4) && ((X,Y) IN %s)'"%(specprefix,pnsrcreg))
	
	os.system("evselect table=pn_clean.fits withspectrumset=yes spectrumset=pn_%s_bkg_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 expression='(FLAG==0) && (PATTERN<=4) && ((X,Y) IN %s)'"%(specprefix,pnbkgreg))

	os.system("backscale spectrumset=pn_%s_spectrum.fits badpixlocation=pn_clean.fits; backscale spectrumset=pn_%s_bkg_spectrum.fits badpixlocation=pn_clean.fits"%(specprefix,specprefix))
		
	os.system("rmfgen spectrumset=pn_%s_spectrum.fits rmfset=pn_%s.rmf"%(specprefix,specprefix))

	os.system("arfgen spectrumset=pn_%s_spectrum.fits arfset=pn_%s.arf withrmfset=yes rmfset=pn_%s.rmf badpixlocation=pn_clean.fits detmaptype=psf"%(specprefix,specprefix,specprefix))

	os.system("specgroup spectrumset=pn_%s_spectrum.fits mincounts=1 oversample=3 rmfset=pn_%s.rmf arfset=pn_%s.arf backgndset=pn_%s_bkg_spectrum.fits groupedset=pn_%s_grp.fits"%(specprefix,specprefix,specprefix,specprefix,specprefix))

	
def makeimages(lowband,highband,bandname):
    lowband = [int(x) for x in lowband.split(',')]
    highband = [int(x) for x in highband.split(',')]
    bandname = [x for x in bandname.split(',')]
 
    for i in range(len(lowband)):
	
        os.system("evselect table=pn_clean.fits imagebinning=binSize imageset=pn_image_%s.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80 expression='(FLAG==0) && (PATTERN<=4) && (PI>%d&&PI<%d)'"%(bandname[i],lowband[i],highband[i]))
        
        os.system("evselect table=m1_clean.fits imagebinning=binSize imageset=m1_image_%s.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=20 yimagebinsize=20 expression='(FLAG==0) && (PATTERN<=12) && (PI>%d&&PI<%d)'"%(bandname[i],lowband[i],highband[i]))
        
        os.system("evselect table=m2_clean.fits imagebinning=binSize imageset=m2_image_%s.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=20 yimagebinsize=20 expression='(FLAG==0) && (PATTERN<=12) && (PI>%d&&PI<%d)'"%(bandname[i],lowband[i],highband[i]))


def ereganalyse():
	inst = ['m1','m2','pn']
	for i in inst:
		
		srcregfile = glob.glob('src_phys.reg'%i)[0]
		with open(srcregfile,'r') as f:
			for line in f:
				pass
			last_line = line
		srcreg = last_line
		print (srcreg)
	
		bkgregfile = glob.glob('bkg75_phys.reg'%i)[0]
		with open(bkgregfile,'r') as f:
			for line in f:
				pass
			last_line = line
		bkgreg = last_line

		os.system("eregionanalyse imageset=%s_image_0p3_10keV.fits bkgimageset=NotSet exposuremap=NotSet srcexp='(X,Y) in %s' backexp='(X,Y) in %s' backval=0 ulsig=0.9973 psfmodel=ELLBETA centroid=yes xcentroid=0 ycentroid=0 optradius=0 optellipxrad=0 optellipyrad=0 optelliprot=0 srccnts=0 status=yes output=%s_eregaoutput_src15.txt withoutputfile=yes -w 1 -V 4"%(i,srcreg,bkgreg,i))


	
sas_setup(firsttime,initodfdir)

if firsttime == 'y':
	emos_analysis()
	epn_analysis()
if makeimg == 'y':
    lowband = input(CYELL+'Enter the lower end of the bands (e.g. enter 200 for 0.2keV or 2000 for 2keV) separated by commas for multiple images: '+CEND)
    highband = input(CYELL+'Enter the higher end of the bands (e.g. enter 200 for 0.2keV or 2000 for 2keV) separated by commas for multiple images:'+CEND)
    bandname = input(CYELL+'Enter suffixes for image names (e.g. X_Y for m1_image_X_Y.fits) separated by commas: '+CEND)
    
    makeimages(lowband,highband,bandname)
if makespec == 'y':
    specprefix = input(CYELL+'Prefix for naming spectral files: '+CEND)
        
    emos_spec(specprefix)
    epn_spec(specprefix)
if reganalyse == 'y':
        ereganalyse()
	


	
	
	

	

	
		

	
	
	
	
