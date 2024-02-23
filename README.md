This repository is based on, please cite below if you use it :

Aly Abdelaziz, Greg M. Baniak, Thomas F. Moslow, Alessandro Terzuoli, Giovanni Grasselli; A novel method for digitizing sedimentological graphic logs and exporting into reservoir modeling software. AAPG Bulletin 2024;; 108 (3): 421–434. doi: https://doi.org/10.1306/10182321114 

The work presented herein proposes a novel approach to digitize the information contained within graphic logs. The digitized data are captured in a manner that allows it to be mapped into various other software. Hence, adopting such an approach provides unprecedented value in terms of harvesting sedimentological and petrographic data and integrating them into various other fields.

The log must be made using computer aided graphics and in PDF format, for e.g., designed using Adobe AI, CorelDraw. Alternatively, the logs maybe drawn on Microsoft Excel or any equivalent spreadsheet software program and exported as PDFs. **The script is not capable of handling scanned papers or scanned files saved as PDFs**.

## CSV Databases

The keywords, symbols, depositional environment are user defined. The user can add to the values in the `defined_color_maps.csv`, `keywords.csv`, and `litho_legend.csv` files. In addition, more symbol templates can be added to the symbols to look for possible matches. 

### defined_color_maps.csv

The red, green, and blue (RGB) color spectrum for the unique set of colors being identified are loaded from external files, located in the same folder as the script `defined_color_maps.csv`.

The file should follow the convention below with a new RGB starting on a new line:

Example file format:

>R,G,B
> 
>210, 180, 140
> 
>244, 164, 96
> 
>135, 206, 235

### keywords.csv

The script will parse the strings encountered in each text box and search for predefined substrings (keywords) when executing in the Text Extraction Mode. These keywords are loaded from external files, located in the same folder as the script `keywords.csv`.

Every word should start on a new line with no trailing spaces:

Example file format:

>Claraia
> 
>Environment
>
>Shoreline

### litho_legend.csv

Each unique color name is a representation of a depositional environment. This information is loaded from an external files, located in the same folder as the script `litho_legend.csv`. 

The file should follow the convention below with a new color starting on a new line:

Example file format:
**Note that there no space between the comma.**

>tan,Bituminous F-M Siltstone
>
>darkkhaki,Bituminous F-M Siltstone
>
>rosybrown,Bituminous F-M Siltstone

# Typical Terminal Output 

An example of an output as it is displayed in the Terminal:

![Terminal Output 01](/sample/sample_Core_1_revised/p1.png)
![Terminal Output 02](/sample/sample_Core_1_revised/p2.png)
![Terminal Output 03](/sample/sample_Core_1_revised/p3.png)

# FAQ

## WAND Error 

If you run into an PIL WAND error, please refer to this link for a possible solution 
https://stackoverflow.com/questions/52699608/wand-policy-error-error-constitute-c-readimage-412

