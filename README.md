Initially, the main objective was to develop a script that can identify lithofacies in the core log lithology column. The identification is based on the colour scheme incorporated in the provided log. An electronic copy of the lithofacies core logging form was provided on May 9, 2018. It is to our understanding that the lithofacies core logging form was prepared using Adobe Illustrator and does not contain any visually evident document control identification pertaining to the layout used.
Additionally, the script was expanded to identify the unconformities and flooding surfaces. The scope also extended to cover template matching to identify the various symbols in the sedimentary structure col-umn and the depositional environments.

## CSV Databases
### defined_color_maps.csv

RGB spectrum for the unique set of colors being identified. The file should follow the conventione below iwth new RGB starting on a new line:

R,G,B

210, 180, 140

### keywords.csv

This contains the keywords that the script will look for when executing in the Text Extraction Mode. 

Every word should start on a new line with no trailing spaces.

### litho_legend.csv

Each "color name" and its corresponding "depositional environment". Note that there no space between the comma.

tan,Bituminous F-M Siltstone

darkkhaki,Bituminous F-M Siltstone

rosybrown,Bituminous F-M Siltstone