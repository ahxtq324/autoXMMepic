# autoXMMepic

# **READ ME!!** 

I have created a script to streamline the XMM processing workflow for my own use, but I hope it will also be useful to others. The code is meant to process observations of extragalactic point sources. \
To run this code from anywhere, you can add an alias in your `~/.bashrc` or `~/.bash_profile` file as: `alias xmmauto='python /path/to/your/xmmauto.py'`

## **Important Notes**

A few things to keep in mind while running the code:

### **0. Before Running the Code:**
- **Helpful Tips**:\
    a. When you download ODF files from the XMM archive for a given observation, they will be in a zipped file.\
    b. Create a new directory (`obsID`) and a subdirectory ('odf') in your preferred folder, such that the path is: `/path/to/your/preferredfolder/obsID/odf`.\
    c. Navigate to the `odf` folder and unzip the downloaded file using: `tar xzvf ../obsID.tar.gz`\
    d. Unzip the new .TAR file as `tar -xvf XXXX_obsID.TAR`. Remove the original *.tar.gz and *TAR files.\
    e. Set your current working directory to the directory where your odf folder resides, i.e. `/path/to/your/preferredfolder/obsID`. The code will make an 
       `analysis` folder in the same directory.
         
- **Initialize HEASoft**, followed by **XMM SAS**.

- Make sure to set your `SAS_CCFPATH` either permanently in your `~/.bashrc` or `~/.bash_profile` file to the directory where your calibration (CCF) files are located, 
           or export it for your current run. Both can be done with `export SAS_CCFPATH=/path/to/your/CCF/files`
 ---

### **1. Initial Questions:**
The script will ask you a few questions at the start.
- If you're analyzing the dataset for the first time and don't have the source and background coordinates, answer **`n`** to the last two questions (spectrum and analysis related) during the initial run. After you have prepared the region files, you may re-run the script and answer **`y`** to the last two questions.\
- If you have everything ready, you may answer **`y`** to all the relevant questions.

---

### **2. Preparing Region Files:**
- Save the region files in **physical coordinates** as `src_phys.reg` and `bkg_phys.reg` using `ds9`.
- The physical coordinates are consistent across all three EPIC cameras, so a single file for the source and background is sufficient.
- **Note:** If the background region overlaps chip gaps in any instrument, you can create separate background regions for different cameras. Name them as `{camera}_bkg_phys.reg`, and update the respective `glob.glob` lines in the code accordingly. (I am currently unsure if regions overlapping with chip gaps is a problem, so this solution is just to be extra careful)
- Ensure the background region is free of any sources.

---
