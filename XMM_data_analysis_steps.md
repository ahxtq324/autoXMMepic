Here is the list of commands and relevant information that I code in the python script.

# XMM DATA ANALYSIS STEPS

### start Heasoft:

`heainit` (or using whatever alias you have for starting it)

### start SAS:

`xmminit` (or using whatever alias you have for starting it)

### Untar all the tar files within the folder and define the SAS_ODF environment variable:

`export SAS_ODF=/my_odf_dir`

### make an analysis directory within your obsID folder and change to that directory - this is where we will store all our analysis data products

`mkdir analysis

cd analysis`

### create a calibration index file and the relative path to this:

`cifbuild` (skip this if you have already the ccf file)

`export SAS_CCF=/full/path/to/analysis/ccf.cif`

### create a summary file of the odf and reset the SAS_ODF variable:

`odfingest` (skip this if you have already the SUM file)

`export SAS_ODF=/full/path/to/ODF/full_name_of_*SUM.SAS`

### reprocess Observation Data Files (ODFs) to obtain calibrated and concatenated event lists (using the most updated calibration):

for pn:  `epchain` or `epproc`

for mos: `emchain` or `emproc`

> OUTPUT: A lot of .FITS files. PXXXX…..EVLI

> =>this will produce the event file for the analysis. The file is in the full-energy range of the instrument and for the entire duration of the observation. It must be filtered to  exclude periods of high-background. 
> I usually rename it: File name: pn.fits or m1.fits or m2.fits

## =========================================================
### 10keV lightcurve for high flares:

> When count rates exceed a given threshold, a warning is issued. The radiation monitor was included on the spacecraft to protect the detectors from penetrating high-energy particles which can damage the detectors. Even with this protection in place many of the X-ray observations suffer from proton flaring.

Following is relevant for single event (i.e. pattern zero only), high energy light curve (for PN camera the energy interval is between 10 and 12 keV), from the event file to identify intervals of flaring particle background  

### for the pn:

`evselect table=pn.fits withrateset=Y rateset=pn_hfl_lc.fits maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='#XMMEA_EP && (PI>10000&&PI<12000) && (PATTERN==0)'`

> OUTPUT: pn_hfl_lc.fits

### for the mos:

`evselect table=m1.fits withrateset=Y rateset=m1_hfl_lc.fits maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='#XMMEA_EM && (PI>10000) && (PATTERN==0)'`

> OUTPUT: m1_hfl_lc.fits

`evselect table=m2.fits withrateset=Y rateset=m2_hfl_lc.fits maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='#XMMEA_EM && (PI>10000) && (PATTERN==0)'`

>OUTPUT: m2_hfl_lc.fits

####  to display the lightcurve: (you can use fv instead! Click on ‘Plot’ option on the RATE row and plot rate vs time) ####  
for the pn:
dsplot table=pn_hfl_lc.fits x=TIME y=RATE
for the mos:
dsplot table=m1_hfl_lc.fits x=TIME y=RATE
####   Determine where the light curve is low and steady. Choose a threshold (count/second) just above the low steady background to define the "low background" intervals (everything that is below 0.4 cts/s for the lightcurve is standard reference. For the RATE parameter we can examine the plot above for non-flared signal. We can use the peak among the non-flared signal as the limit for the RATE parameter) and produce the relative file ####  
for the pn:
tabgtigen table=pn_hfl_lc.fits expression='RATE<=0.4' gtiset=pn_gti.fits 
OUTPUT: pn_gti.fits
for the mos:
tabgtigen table=m1_hfl_lc.fits expression='RATE<=0.35' gtiset=m1_gti.fits
OUTPUT: m1_gti.fits
tabgtigen table=m2_hfl_lc.fits expression='RATE<=0.35' gtiset=m2_gti.fits
OUTPUT: m2_gti.fits

####  produce the filtered event file excluding the period of flaring background and selecting energies above 0.15 keV  ####  
for pn:
evselect table=pn.fits withfilteredset=Y filteredset=pn_clean.fits destruct=Y keepfilteroutput=T expression='#XMMEA_EP && gti(pn_gti.fits,TIME) && (PI>150)'
OUTPUT: pn_clean.fits
for mos:
evselect table=m1.fits withfilteredset=Y filteredset=m1_clean.fits destruct=Y keepfilteroutput=T expression='#XMMEA_EM && gti(m1_gti.fits,TIME) && (PI>150)'
OUTPUT: m1_clean.fits
evselect table=m2.fits withfilteredset=Y filteredset=m2_clean.fits destruct=Y keepfilteroutput=T expression='#XMMEA_EM && gti(m2_gti.fits,TIME) && (PI>150)'
OUTPUT: m2_clean.fits
=> at this point you have a filtered file (pn_clean.fits) which will be use to extract lightcurves, images and spectra.
=========================================================
Images:
####  extract an image in the full energy range of the filtered event file (>0.15 keV)  ####  
for the pn:
evselect table=pn_clean.fits imagebinning=binSize imageset=pn_image.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80
OUTPUT: pn_image.fits
for the mos:
evselect table=m1_clean.fits imagebinning=binSize imageset=m1_image.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80
OUTPUT: m1_image.fits
evselect table=m2_clean.fits imagebinning=binSize imageset=m2_image.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80
OUTPUT: m2_image.fits
####  extract an image in a selected energy range (e.g. 0.3-10 keV). In this example some filters are also included (e.g. FLAG==0 and PATTERN<=4, which select only single and double pixel events)  ####  
for the pn:
evselect table=pn_clean.fits imagebinning=binSize imageset=pn_image_0.3_10.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=82 yimagebinsize=82 expression='(FLAG==0) && (PATTERN<=4) && (PI>300&&PI<10000)'
OUTPUT: pn_image_0.3_10.fits
for the mos:
evselect table=m1_clean.fits imagebinning=binSize imageset=m1_image_0.3_10.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=22 yimagebinsize=22 expression='(FLAG==0) && (PATTERN<=12) && (PI>300&&PI<10000)'
OUTPUT: m1_image_0.3_10.fits
evselect table=m2_clean.fits imagebinning=binSize imageset=m2_image_0.3_10.fits withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=22 yimagebinsize=22 expression='(FLAG==0) && (PATTERN<=12) && (PI>300&&PI<10000)'
OUTPUT: m2_image_0.3_10.fits
####  to display (or simply with ds9)  ####  
imgdisplay withimagefile=true imagefile=pn_image.fits
=========================================================
Source/Background region file & Spectrum:
####  select the source and bkg regions. Coordinates and radius has to be set to 'physical'  ####   
#Background region should be on the same ccd and possibly a region  without field sources and at the same distance to the readout node (RAWY position) as the source region. Shape and area of the src and bkg region can be different.
#your region file should be, for example (the radius is 30 arcsec):
more src_pn.reg
# Region file format: DS9 version 4.1
global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1
physical
circle(26245.063,27937.004,600)
####  source spectrum  ####
for the pn:
evselect table=pn_clean.fits withspectrumset=yes spectrumset=pn_src_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 expression='(FLAG==0) && (PATTERN<=4) && ((X,Y) IN circle(26245.063,27937.004,600))'
OUTPUT: pn_src_spectrum.fits 
for the mos:
evselect table=m1_clean.fits withspectrumset=yes spectrumset=m1_src_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 expression='#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN circle(26245.063,27937.004,600))'
OUTPUT: m1_src_spectrum.fits
evselect table=m2_clean.fits withspectrumset=yes spectrumset=m2_src_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 expression='#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN circle(26245.063,27937.004,600))'
OUTPUT: m2_src_spectrum.fits
####  same for the bkg spectrum for the relative region  ####
for the pn:
evselect table=pn_clean.fits withspectrumset=yes spectrumset=pn_bkg_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 expression='(FLAG==0) && (PATTERN<=4) && ((X,Y) IN circle(27882.271,25577.004,1546.4296))'
OUTPUT: pn_bkg_spectrum.fits
for the mos:
evselect table=m1_clean.fits withspectrumset=yes spectrumset=m1_bkg_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 expression='#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN circle(27882.271,25577.004,1546.4296))'
OUTPUT: m1_bkg_spectrum.fits
evselect table=m2_clean.fits withspectrumset=yes spectrumset=m2_bkg_spectrum.fits energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 expression='#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN circle(27882.271,25577.004,1546.4296))’
OUTPUT: m2_bkg_spectrum.fits
####  calculate the area for src and bkg region  ####
for the pn:
backscale spectrumset=pn_src_spectrum.fits badpixlocation=pn_clean.fits
backscale spectrumset=pn_bkg_spectrum.fits badpixlocation=pn_clean.fits
for the mos:
backscale spectrumset=m1_src_spectrum.fits badpixlocation=m1_clean.fits
backscale spectrumset=m1_bkg_spectrum.fits badpixlocation=m1_clean.fits
backscale spectrumset=m2_src_spectrum.fits badpixlocation=m2_clean.fits
backscale spectrumset=m2_bkg_spectrum.fits badpixlocation=m2_clean.fits
####  generate the rmf file  ####
for the pn:
rmfgen spectrumset=pn_src_spectrum.fits rmfset=pn.rmf
OUTPUT: pn.rmf
for the mos:
rmfgen spectrumset=m1_src_spectrum.fits rmfset=m1.rmf 
OUTPUT: m1.rmf
 rmfgen spectrumset=m2_src_spectrum.fits rmfset=m2.rmf
OUTPUT: m1.rmf
####  generate the arf file (for a point-like source)  ####  
for the pn:
arfgen spectrumset=pn_src_spectrum.fits arfset=pn.arf withrmfset=yes rmfset=pn.rmf badpixlocation=pn_clean.fits detmaptype=psf
OUTPUT: pn.arf
for the mos:
arfgen spectrumset=m1_src_spectrum.fits arfset=m1.arf withrmfset=yes rmfset=m1.rmf badpixlocation=m1_clean.fits detmaptype=psf
OUTPUT: m1.arf
arfgen spectrumset=m2_src_spectrum.fits arfset=m2.arf withrmfset=yes rmfset=m2.rmf badpixlocation=m2_clean.fits detmaptype=psf
OUTPUT: m2.arf
####  group the src, bkg and response file together, rebin to have a minimum number of counts (e.g. 20) for each channel (bkg-subtracted) and not to oversample the intrinsic energy resolution by a factor larger then 3  ####  
for the pn:
specgroup spectrumset=pn_src_spectrum.fits mincounts=1 oversample=3 rmfset=pn.rmf arfset=pn.arf backgndset=pn_bkg_spectrum.fits groupedset=pn_spectrum_grp.fits
OUTPUT: pn_spectrum_grp.fits
for the mos:
specgroup spectrumset=m1_src_spectrum.fits mincounts=1 oversample=3 rmfset=m1.rmf arfset=m1.arf backgndset=m1_bkg_spectrum.fits groupedset=m1_spectrum_grp.fits
OUTPUT: m1_spectrum_grp.fits
specgroup spectrumset=m2_src_spectrum.fits mincounts=1 oversample=3 rmfset=m2.rmf arfset=m2.arf backgndset=m2_bkg_spectrum.fits groupedset=m2_spectrum_grp.fits
OUTPUT: m2_spectrum_grp.fits
the final file: pn_spectrum_grp.fits is ready for Xspec!
