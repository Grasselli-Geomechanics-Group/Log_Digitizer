# /////////////////////////////////////////////////////////////// #
# !python3.6
# -*- coding: utf-8 -*-
# Python Script initially created on 12/05/2018
# Compiled by Aly @ Grasselli's Geomechanics Group, UofT, 2018
# Created using PyCharm // Tested on Spyder
# Current Version 06 - Dated July 31, 2018
# /////////////////////////////////////////////////////////////// #

## This code was compiled based on the layout of d_66_I_94_B_16_Continuous_Core Log

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import resolve1
from PyPDF2 import PdfFileWriter, PdfFileReader
from scipy import spatial
from collections import OrderedDict
from operator import itemgetter
from itertools import permutations
from scipy.spatial import distance
from PIL import Image
from collections import Counter
import numpy as np
import pdfminer
import time
import os
import imutils
import cv2
import random
import webcolors
import csv

# START OF EXECUTION
abs_start = time.time()

# Locations of items to look for. Format {"WHAT" : [X coordinate from left of log, Y coordinate from top of log]}
locations = {'Name:' : [475, 56], 'Well Location:' : [100, 42] , 'Fm/Strat. Unit:' : [308, 56], 'Date:' : [469, 84]}

# Abbreviation of the Dep. Env. / Sedimentary Facies
# Will display an error if the text recognised in the Env. column is not in this list.
env_list = ['H', 'O', 'OTD', 'OTP', 'T. Lag', 'Ramp', 'Distal Ramp', 'T', 'Temp', 'OT', 'LS', 'Turb', 'Temps', 'Seismite', 'Fluidized Flow']

# Resolutions
h_resol = 600
resol = 300

## DICTIONARY
litho_legend = {"skyblue": "Laminated Bedded Resedimented Bioclasts", "sandybrown": "Bituminous F-C Siltstone", "tan": "Bituminous F-M Siltstone", "khaki": "Sandy F-C Siltstone to Silty VF Sandstone", "darkseagreen": "Phosphatic - Bituminous Sandy Siltstone to Breccia", "plum": "Calcareous - Calcispheric Dolosiltstone", "white": "Blank Space"}
excluded_colors = [(255, 255, 255), (36, 31, 33), (94, 91, 92), (138, 136, 137), (197, 195, 196), (187, 233, 250), (26, 69, 87)]  # exclusion colors from mapping [(White), (Black), (Dim Grey), (Grey), (Silver), (paleturquoise), (darkslategray)]
defined_color_map = [(201, 163, 127), (250, 166, 76), (122, 176, 222), (255, 245, 135), (199, 161, 201), (156, 212, 173), (255, 255, 255)]

# RGB: (201, 163, 127) 	- Closest RGB colour name: tan!
# RGB: (250, 166, 76) 	- Closest RGB colour name: sandybrown!
# RGB: (122, 176, 222) 	- Closest RGB colour name: skyblue!
# RGB: (255, 245, 135) 	- Closest RGB colour name: khaki!
# RGB: (199, 161, 201) 	- Closest RGB colour name: plum!
# RGB: (156, 212, 173) 	- Closest RGB colour name: darkseagreen!

'''
TIMER FUNCTION
'''


def calc_timer_values(end_time):
    minutes, sec = divmod(end_time, 60)
    if end_time < 60:
        return "\033[1m%.2f seconds\033[0m" % end_time
    else:
        return "\033[1m%d minutes and %d seconds\033[0m." % (minutes, sec)

'''
FORMATTING OPTIONS

- TEXT COLORS
'''


def red_text(val): # RED Bold text
    tex = "\033[1;31m%s\033[0m" % val
    return tex


def green_text(val): # GREEN Bold text
    tex = "\033[1;92m%s\033[0m" % val
    return tex


def bold_text(val): # Bold text
    tex = "\033[1m%s\033[0m" % val
    return tex

'''
DEFINE THE RGB SPECTRUM FOR VISUAL APPEAL
'''


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


'''
GET COLOR NAME BASED ON RGB SPECTRUM

- If not found returns nearest color name in spectrum
'''


def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name

'''
CONVERT BYTES TO STRING

- Default PDF reader usually return  unicode string.
- Convert the given unicode string to a bytestring, using the standard encoding, unless it's already a bytestring.
'''


def to_bytestring (s, enc='utf-8'):
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)

'''
GLOBAL OPENING OF FILE

- Insert File name to open
- Load file
'''

# Open a PDF file.
# pdf_name = '/home/aly/Desktop/log2/d_66/d_66_I_94_B_16_Continuous_Core.pdf'
# pdf_name = '/home/aly/Desktop/log2/talisman/Talisman c-65-F_Page 1.pdf'
# pdf_name = 'C:/Users/alica/Desktop/log2/d_66/d_66_I_94_B_16_Continuous_Core.pdf'
# pdf_name = 'C:/Users/alica/Desktop/log2/talisman/Talisman_c-65-F_Page_1.pdf'
# pdf_name = "C:/Users/alica/Desktop/log2/lily/Lily a-9-J_Core 2_Page 4 of 13.pdf"
pdf_name = "/home/aly/Desktop/log2/lily/Lily a-9-J_Core 2_Page 4 of 13.pdf"

# LOAD FILE
fp = open(pdf_name, 'rb')

# def update_page_text_hash (h, lt_obj, pct=0.2):
#     """Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""
#     x0 = lt_obj.bbox[1]
#     x1 = lt_obj.bbox[3]
#     key_found = False
#     for k, v in h.items():
#         hash_x0 = k[1]
#         if x0 >= (hash_x0 * (1.0-pct)) and (hash_x0 * (1.0+pct)) >= x0:
#             hash_x1 = k[0]
#             if x1 >= (hash_x1 * (1.0-pct)) and (hash_x1 * (1.0+pct)) >= x1:
#                 # the text inside this LT* object was positioned at the same
#                 # width as a prior series of text, so it belongs together
#                 key_found = True
#                 v.append(to_bytestring(lt_obj.get_text()))
#                 h[k] = v
#     if not key_found:
#         # the text, based on width, is a new series,
#         # so it gets its own series (entry in the hash)
#         h[(x0,x1)] = [to_bytestring(lt_obj.get_text())]
#     return h

'''
PROCESS // PARSE ALL PDF

- Loops over ALL the identified elements in the PDF
- Obtains their bounding box
'''


def parse_obj(lt_objs):
    coord, corel, depths = [], {}, {}
    y_loc = tot_len - 190

    '''
    PROCESS // PARSE DEPTH ALL DATA
    
    - Y is captured as the mid-height of the bounding box.
    '''

    # bbox(bounding box) attribute of a textbox, is a four-part tuple of the object's page position: (x0, y0, x1, y1)
    # position is returned in terms of Pt. units. Where 0 is the bottom-right of the page.
    for obj in lt_objs:
        # if it is a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            y_mid_height = (obj.bbox[1] + obj.bbox[3]) / 2
            print("%6d, %6d, %6d, %6d, => %6d - %6d => dx=%6d dy=%6d - %s" % (obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3], obj.bbox[0], y_mid_height, obj.bbox[2] - obj.bbox[0], obj.bbox[3] - obj.bbox[1],  obj.get_text().replace('\n','_')))  # Print all OCR Matches and the bounding box locations.
            coord.append([obj.bbox[0], y_mid_height ])  # List of all X/Y of bounding boxes. Y is mid/height.
            corel[obj.get_text().replace('\n', '_')] = [obj.bbox[0], y_mid_height]  # Dictionary of {TEXT : [X , Y]}
        # if it is a container, recurse. That is, LTFigure objects are containers for other LT* objects, so recurse through the children
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs)

    print(green_text("PDF OCR COMPLETED. \n"))

    # Run the module to obtain scale.
    log_info(coord, corel)

    '''
    PROCESS // PARSE DEPTH COLUMN
    
    - Lookup depth column (X = 40 to 60 & Y = 180 points from top of page).
    - Identifies presence of integers to establish scale.
    - Returns error is anything apart from integers is encountered.
    '''

    for obj in lt_objs:
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            if int(obj.bbox[0]) in range(40,60) and int(obj.bbox[1]) < y_loc:
                # Checks for integers, produces error and continues if non-integer encountered
                try:
                    y_mid_height = (obj.bbox[1] + obj.bbox[3]) / 2
                    depths[int(y_mid_height)] = int(obj.get_text().replace('\n', ''))
                except ValueError:
                    print(red_text("Error in Depth Column\nPossible text detected:\t %s" % obj.get_text().replace('\n', '_')))
                    # exit("Status 10 - Text identified in the Depth Column. Please change value of y_loc.")


    # Sort by location in the column
    # Separate the OCR depth from the point location
    depths = OrderedDict(sorted(depths.items(), key=lambda t: t[0]))
    a, b = [], []

    for key in depths:
        a.append(depths[key])
        b.append(key)

    # Load module to check information in depth column
    list_a = check_depth_column('Depths Values', a)
    list_b = check_depth_column('Pt. Location', b)

    # Improvement - How can this difference be quantitative? Standard Deviation?
    # import statistics
    # print(statistics.stdev([(x*1.0) / y for x,y in zip(list_a, list_b)]))

    # Equation of linear correlation between
    # OCR depth [a] & Pt. location [b]
    # between second and second last to avoid movement of last depth avoiding extension of page
    # Itendified in Lily log.
    y, x = [a[1], a[-2]], [b[1], b[-2]]
    coeff(x, y)

    # DISPLAY the entire depth column matches {DEPTH : VALUE}
    print(green_text("\nProcessed Depth Column - OCR Mode.\nCoeff : %.3f x + %.3f.\n" % (m, c)))
    print("Pt. : OCR Depth value")
    for key in depths:
        print("%s : %s" % (key, depths[key]))  # DISPLAY the OCR of the text sequence {Pt. : OCR Depth value}
    # print(green_text("\nProcessed Depth Column - OCR Mode.\nCoeff : %s x + %s.\n" % (m, c)))


    '''
    PROCESS // PARSE ENVIRONMENT COLUMN

    - Lookup depth column (X = 524 to 535 & Y = 180 points from top of page).
    - Identifies presence of information in the column.
    - If text has more than one manual enter, split on the '_'. And in any case remove the last '_'
    - In that case, adjust the X location to match the start of a new line. Estimated as 16.3 points.
    - After parsing the data:
        - If has "/" then two environments. 
        - Lookup environments in the predefined dictionary.
        - In case of two environments; will check both.
    - Will show error if it can not understand the text OR the "/" is at the start or end of the string.
    '''

    texts, dys = {}, []
    for obj in lt_objs:
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            if int(obj.bbox[0]) in range(520, 535) and int(obj.bbox[1]) < y_loc:
                # text, location = "%.3f, %s" % (m * obj.bbox[1] + c, obj.get_text().replace('\n', '_'))
                # print("%.3f, %s" % (m * obj.bbox[1] + c, obj.get_text().replace('\n', '_')))
                # d = m * obj.bbox[1] + c
                y_mid_height = (obj.bbox[1] + obj.bbox[3]) / 2
                texts[m * y_mid_height + c] = obj.get_text().replace('\n', '_')
                if obj.get_text().replace('\n', '_').count('_') == 1:
                    dys.append(abs(obj.bbox[1] - obj.bbox[3]))
                # print(obj.bbox[1], obj.bbox[1] / ratio, obj.get_text().replace('\n', '_'))

    # for k,v in texts.items():
    #     print(k,v)
    dy = sum(dys) / len(dys)

    split_texts, deleted_keys = {}, []
    print(bold_text("\nValidating OCR in Environment Column\n"))
    for key, v in list(texts.items()):
        if v.count("_") > 1 and v not in ["Distal_Ramp_"]:
            print("Manual \'Enter\' detected - %s" % v)
            underscore_list = v.split("_")  # Split on '_'
            underscore_list.pop()  # Remove the last '_'
            del texts[key]  # Delete that key from the dictionary
            # deleted_keys.append(key)
            # Adjust X based on the number of manual enters within the text box.
            for loc, i in enumerate(underscore_list):
                delta = (m * dy) * ((len(underscore_list) - loc) - (len(underscore_list) / 2) - 0.5)
                texts[key + delta] = i
                # delta = (len(underscore_list) / 2 - 1 - loc) * (m * (14)) # 16.3
        else:
            if v.endswith('_'):
                v = v[:-1]
                texts[key] = v.replace('_', ' ')
            # else:
            #     texts[key] = v.replace('_', ' ')

    comb = permutations(env_list, 2)
    global env_matches
    env_matches = {}
    for k,v in texts.items():
        if v in env_list:
            # print("Match %0.3f - %s" % (k, v))
            env_matches[k] = v
        elif '/' in v:
            print('Possibly Dual Environment \t %0.3f - %s' % (k, v))
            a = v.split('/')
            print(red_text('Found Possible matches %s') % ' and '.join(a))
            env_matches[k] = ' / '.join(a)
            for i in a:
                if i in env_list or i == '':
                    continue
                #     print("SUB - Match %0.3f - %s" % (k, i))
                #     # env_matches[k] = i
                # elif i == '':
                #     # print("Empty String")
                #     continue
                else:
                    print(bold_text('PLEASE CHECK! %s') % red_text(i))
                    for b in list(comb):
                        n = ''.join(b)
                        if i == n:
                            print(red_text('Found Possible matches %s') % ' and '.join(b))
                            env_matches[k] = ' / '.join(b)
        else:
            print('UNKNOWN %0.3f - %s' % (k, v))
        # print(k,v)

    env_matches = OrderedDict(sorted(env_matches.items()))
    # print(env_matches)
    # DISPLAY the entire environment matches {DEPTH : VALUE}
    print(green_text("\nProcessed Environments - OCR Mode\n"))
    print(env_matches)
    print('Depth (m) : Environment')
    for key in env_matches:
        print("%.5f : %s" % (key, env_matches[key]))
    # exit (10)


    # Identify location of lines

    # img = cv2.imread('/home/aly/Desktop/log1/env_log_python_convert.png')
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # edges = cv2.Canny(gray,50,150,apertureSize = 3)
    #
    # lines = cv2.HoughLines(edges,1,np.pi/180,200)
    # for rho,theta in lines[0]:
    #     a = np.cos(theta)
    #     b = np.sin(theta)
    #     x0 = a*rho
    #     y0 = b*rho
    #     x1 = int(x0 + 1000*(-b))
    #     y1 = int(y0 + 1000*(a))
    #     x2 = int(x0 - 1000*(-b))
    #     y2 = int(y0 - 1000*(a))
    #
    #     cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
    #
    # cv2.imwrite('houghlines3.jpg',img)

'''
LOG INFO

- Obtains important information from the log.
- Locations are returned based on the "locations' dictionary
'''

## Possible Improvement
# 1) Make the match not on X/Y but on the next X in the line (Same Y Value).
# 2) Does not work if there is a  manual enter by the user in the log.


def log_info(coord, corel):
    coord_myarray = np.asarray(coord)  # convert nested list to numpy array
    for k, v in locations.items():  # Load locations of identified text
        v[1] = tot_len - v[1]  # Get the depth from the top.
        alpha = coord_myarray[spatial.KDTree(coord_myarray).query(v)[1]]  # Lookup nearest point to predefined location
        for k1, v1 in corel.items():  # Load the correlation dictionary
            if v1 == list(alpha):  # Lookup position matches and return matching information.
                if k1.count("_") > 1:
                    print(bold_text(k), '\t', k1.split('_')[0])
                else:
                    print(bold_text(k), '\t', k1.replace('_', ''))

'''
DEPTH COLUMN - VALIDATION

- Checks depth column for 
1) Value of depth (makes sure it is an integer)
2) Ensures that they are in descending order
3) Check the ratio (i.e. difference between the depths and their location on the log)
'''

## Improvement
# 1) Make the comparison of teh ratio by d_depth over d_point.
# How can this difference be quantitative - Standard Deviation / COV?
# What constituents bad//good.

def check_depth_column(name, list_values):
    if name == 'Depth Values':
        # list_values = list(reversed(list_values))
        for x, i in enumerate(list_values):
            if x < len(list_values) - 1 :
                    if list_values[x] < list_values[x + 1]:
                        print("Check the depth values for Typos")
                        # exit(11)
    unique_values = len(set(np.diff(list_values)))
    # diff = abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values))))
    if len(set(np.diff(list_values))) == 1 or abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values)))) < 2:
         print(green_text("\n%s in the DEPTH COLUMN CHECKED" % name))
    # elif abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values)))) < 2:
    #     print("MINOR Error in scale of %s, off by %s units" % (name, diff))
    else:
        print(red_text("Status 12 - Possible error in scale of %s.\nValues are %s" % (name, np.diff(list_values))))
        # exit("Status 12 - MINOR Error in scale of %s, off by %s units\nValues are %s" % (name, diff, np.diff(list_values)))
    return np.diff(list_values)


'''
INITIALIZING MAIN MODULE FOR EXECUTION

- SCRIPT OBTAINED FROM https://stackoverflow.com/questions/22898145/how-to-extract-text-and-text-coordinates-from-a-pdf-file
- Open PDF and obtain file extents. Mainly "y_top" that will be used for further processing.
- Size of MEDIABOX returned in points.
'''


def initial_processing():
    global tot_len
    print("LOADING %s. Please be patient..." % red_text(os.path.basename(pdf_name)))
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)

    # Create a PDF document object that stores the document structure.
    # Password, if any, for initialization as 2nd parameter
    document = PDFDocument(parser)

    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()

    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)

    # BEGIN LAYOUT ANALYSIS
    # Set parameters for analysis.
    laparams = LAParams()

    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Total number of pages in PDF.
    tot_pages = (resolve1(document.catalog['Pages'])['Count'])
    page_count = 1

    # loop over all pages in the document
    for page in PDFPage.create_pages(document):

        # read the media box that is the page size as list of 4 integers x0 y0 x1 y1
        print("PAGE %s DIMENSIONS is %s points." % (page_count, page.mediabox))
        _, _, _, tot_len = page.mediabox

        # read the page into a layout object
        # receive the LTPage object for this page
        interpreter.process_page(page)
        # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
        layout = device.get_result()

        # load module to parse every object encountered in the PDF
        print("PDF PAGE %s / %s LOADED." % (page_count, tot_pages))
        parse_obj(layout._objs)

        # Convert PDF to process lithology column and obtain Pt./Pixel Ratio
        processing(defined_color_map)

        # Crop PDF to precess the biogenic column
        cropping_pdf()

        # Increase page count
        page_count += 1


'''
CONVERT PDF TO PNG

- Loads PDF log and returns PNG at specified pixel
'''

def convert(f_name, conv_resol):
    global fil_name
    from wand.image import Image
    from wand.color import Color
    with Image(filename=f_name, resolution=conv_resol) as img:
        with Image(width=img.width, height=img.height, background=Color("white")) as bg:
            bg.composite(img, 0, 0)
            bg.save(filename=os.path.splitext(f_name)[0] + '_python_convert.png')
    fil_name = os.path.splitext(f_name)[0] + '_python_convert.png'

'''
LOAD FOLDER

- Load folder that contains all the templates to be matched.
'''


def load_templates(template_folder):
    templates_folder = []
    for root, path_dir, filenames in os.walk(template_folder):
        for filename in filenames:
            templates_folder.append(os.path.join(root, filename))
    templates_folder = sorted(templates_folder)
    return templates_folder


'''
CROP PDF
    # - Load entire PDF
    # - Crop off PDF and return new MediaBOX bound PDF.
    # - Convert that MediaBOX into high resolution for better image match.
'''

def cropping_pdf():
    with open(pdf_name, "rb") as in_f:
        log_input = PdfFileReader(in_f)
        x1, y1, x2, y2 = log_input.getPage(0).mediaBox
        numpages = log_input.getNumPages()
        sed_struc_log_output = PdfFileWriter()

        # Crop off the sed_biogenic column
        for i in range(numpages):
            sed_struc_log = log_input.getPage(i)
            sed_struc_log.mediaBox.lowerLeft = (240, y2)
            sed_struc_log.mediaBox.upperRight = (215, y1)
            sed_struc_log_output.addPage(sed_struc_log)

        # Write cropped area as a new PDF
        with open((os.path.join(os.path.dirname(os.path.splitext(pdf_name)[0]), "sed_struc_log.pdf")), "wb") as out_f:
            sed_struc_log_output.write(out_f)
        out_f.close()

        # Open PDF and convert to PNG (h_resol) for image processing.
        out_f = (os.path.join(os.path.dirname(os.path.splitext(pdf_name)[0]), "sed_struc_log.pdf"))
        convert(out_f, h_resol)

        # Load image, template folder and execute matching module using biogenic parameters and threshold
        cropped_pdf_image = (os.path.join(os.path.dirname(os.path.splitext(pdf_name)[0]), "sed_struc_log_python_convert.png"))
        template_folder = os.path.join((os.path.dirname(os.path.splitext(pdf_name)[0])), "templates")
        matching(cropped_pdf_image, template_folder, 0.70)  # match => pdf_image, folder holding template, matching threshold

'''
MATCH IMAGE & DISPLAY RESULT

- Match the templates from the folder to their respective locations within the cropped image.
- Templates are resized from 90 -110% of their size to look for more matches.
- During matching the ratio of tracking is tracked.
- Match proximity of based on half the smallest diagonal of the all template image.. 
'''


def matching(match_fil_name, folder, threshold):
    matched, temp_locations = {}, []
    templates_folder = load_templates(folder)  # Load Templates from Folder
    print(green_text("\nProcessing %s - PNG Mode\nFound %s templates in folder" % (os.path.basename(folder).upper(), len(templates_folder))))
    img_bgr = cv2.imread(os.path.abspath(match_fil_name))  # Read Image as RGB
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)  # Convert Image to grayscale
    cv2.imwrite(os.path.join(os.path.dirname(match_fil_name), 'gray_image.png'), img_gray)  # Write binary Image
    _, temp_w, temp_h = img_bgr.shape[::-1]  # Tuple of number of rows, columns and channels
    # print(img_bgr.size)
    # dpi = int(img_bgr.size / (temp_w * temp_h) * 100)
    print ("\nImage Loaded - Dimensions %s px X %s px @ %s dpi.\nPixel to Point ratio is: %.2f" % (temp_w, temp_h, h_resol, ratio_px_pt))

    global unique_loc
    remove, unique_loc = [], []  # reset every time loop is initialised?
    list_r = []

    # Lookup every image in the template folder.
    for count, name in enumerate(templates_folder):
        # remove, unique_loc, = [], []  #reset every time loop is initialised
        color = list([random.choice(range(0, 256)), random.choice(range(0, 256)), random.choice(range(0, 256))])  # Random Color choice
        template = cv2.imread(os.path.abspath(name), 0)  # Read Template Image as RGB
        # template = imutils.resize(template, width=int(template.shape[1] * 2))
        w, h = template.shape[::-1]
        r = ((h**2 + w **2) ** 0.5)
        list_r.append(r / 2)
        # resize the image according to the scale, and keep track of the ratio of the resizing
        max_scale, min_scale = 1.3, 0.7
        spacing = int((max_scale - min_scale) / 0.1)
        for scale in np.linspace(min_scale, max_scale, spacing + 1)[::-1]:
            # resize the image according to the scale, and keep track of the ratio of the resizing
            resized = imutils.resize(template, width=int(template.shape[1] * scale))
            # r = template.shape[1] / float(resized.shape[1]) #ratio
            res = cv2.matchTemplate(img_gray, resized, cv2.TM_CCOEFF_NORMED)  # Match template to image using normalized correlation coefficient
            loc = np.where(res >= threshold)  # Obtain locations, where threshold is met. Threshold defined as a function input
            for pt in zip(*loc[::-1]):  # Goes through each match found
                temp_locations.append(pt)

        # Sort matches based on Y location.
        temp_locations = sorted(temp_locations, key=itemgetter(1, 0))

    # Look for the unique points.
    # Minimum distance between matches set as half the smallest diagonal of the all template image.
    unique = recursiveCoord(temp_locations, min(list_r))
    unique = sorted(unique, key=itemgetter(1, 0))

    # Draw a color coded box around each matched template.
    for pt in unique:
        # print("unique", pt, (pt[0] ** 2 + pt[1] ** 2) ** 0.5)
        cv2.rectangle(img_bgr, pt, (pt[0] + w, pt[1] + h), color, 2)
        unique_loc.append(pt[1])

    print("Found %s matches." % bold_text(len(unique)))

    # Write image showing the location of the detected matches.
    output_file_name = str(os.path.basename(folder)) + '_detected %s' % os.path.basename(name)
    cv2.imwrite(os.path.join(os.path.dirname(match_fil_name), output_file_name), img_bgr)
    print(bold_text("Detected image saved.\n"))

    write_to_csv(overall_dictionary, env_matches, color_dict, unique_loc)

'''
CHECKING PROXIMITY

- Takes the first X/Y of the matched points and compares it to the remaining points.
- Points within the threshold are deleted and the list updated. 
- Iterates till all the points are compared against each other. 
'''

def recursiveCoord(_coordinateList, threshold):
    if len(_coordinateList) > 1:
        xy_0 = _coordinateList[0]
        remaining_xy = list(set(_coordinateList) - set(xy_0))

        new_xy_list = []

        for coord in remaining_xy:
            dist = distance.euclidean(xy_0 ,coord)

            if dist >= threshold:
                new_xy_list.append(coord)

        return [xy_0] + recursiveCoord(new_xy_list, threshold)
    else:
        return []

'''
CONVERT PDF TO PNG

- Loads PDF log and returns PNG at specified pixel
'''


def convert(f_name, conv_resol):
    global fil_name
    from wand.image import Image
    from wand.color import Color
    with Image(filename=f_name, resolution=conv_resol) as img:
        with Image(width=img.width, height=img.height, background=Color("white")) as bg:
            bg.composite(img, 0, 0)
            bg.save(filename=os.path.splitext(f_name)[0] + '_python_convert.png')
    fil_name = os.path.splitext(f_name)[0] + '_python_convert.png'


'''
INITIALISATION

- Loads Image
- Obtains all colors (1 pixel wide) at X location
- Reduces colors to an amount equal to the user defined unique colors
'''


# - Loads Image

def load_image(file_name):
    global rgb_im, width, height
    # Image.MAX_IMAGE_PIXELS = None # Override to PIXEL processing limitation. This will tremendously increase processing time.
    # Load Image
    im = Image.open(file_name)
    # Convert to RGB
    rgb_im = im.convert('RGB')
    # Obtain image dimension for digitization
    width, height = im.size
    # pdf_image = cv2.imread(file_name)  # Read Image as RGB
    # _, pdf_dpi_w, pdf_dpi_h = pdf_image.shape[::-1]  # Tuple of number of rows, columns and channels
    # pdf_dpi = int(pdf_image.size / (pdf_dpi_w * pdf_dpi_h) * 100)
    # cv2.destroyAllWindows()
    return rgb_im, width, height


def ratio():
    global ratio_px_pt
    ratio_px_pt = height / tot_len
    return ratio_px_pt

def coeff(mx, my):
    global m, c
    m, c = np.polyfit(mx, my, 1)
    return m, c


def processing_HZ_lines():
    HZ_lines = {}
    print ("\nImage Loaded - Dimensions %s px X %s px @ dpi.\nPixel to Point ratio is: %.3f" % (width, height, ratio_px_pt))
    approx_x = {1530: ['ALL_PNG', 745, 1], 2370: ['ENV_PNG', 100, 100]} # FATAL ERROR IS TRACED To HERE!

    for k, v in approx_x.items():
        location_to_check = []
        black_lines = []
        for j in range(0, height):
            print(j, rgb_im.getpixel((1530, j)))
            if rgb_im.getpixel((k, j)) == (36, 31, 33):
                black_lines.append(int(j))

        for i in black_lines:
            print(i)
        # print(black_lines)
        possible_black_lines = ((group_runs(black_lines)))
        # for i in possible_black_lines:
        #     print(i)
        for i in possible_black_lines:
            print(i)
            location_to_check.append((sum(i) / len(i)))
        print(height)

        # exit(100)
        bed(k, v[1], v[2], location_to_check)
        HZ_lines[v[0]] = contact_type


    # print(HZ_lines)

    ALL_PNG = (HZ_lines['ALL_PNG'])
    ENV_PNG = (HZ_lines['ENV_PNG'])

    print(ALL_PNG)
    # exit(100)
    if len(ALL_PNG) == len(ENV_PNG):
        for x in range(len(ALL_PNG)):
            if -10 < ALL_PNG[x] - ENV_PNG[x] < 10:
                continue
                # print(ALL_PNG[x] - ENV_PNG[x], "match")
            else:
                print(ALL_PNG[x], ENV_PNG[x], "Non match")
    else:
        print(red_text("LINE IN ALL PNG AND ENV PNG DO NOT MATCH"))
        print(list(set(ALL_PNG) - set(ENV_PNG)))
        exit("FATAL ERROR!")

    final_dict = {}

    zipped = list(zip(ALL_PNG, ALL_PNG[1:]))
    # zipped.append((ALL_PNG[-1], c))
    print(zipped)
    # time.sleep(10)
    # ALL_PNG.pop()

    for a, x in enumerate(ALL_PNG):
        if a < (len(ALL_PNG) - 1 ):
            print(x, zipped[a])
            final_dict[x] = list(zipped[a])

    # for i in ALL_PNG:
    #     final_dict[ALL_PNG[i]] = list(zipped[i])

    # exit (110)
    # print(sorted(final_dict), key)
    global  overall_dictionary

    overall_dictionary = OrderedDict(sorted(final_dict.items()))

    print(dict(overall_dictionary))
    # ALL_PNG = list(HZ_lines[0][:])
    # print(ALL_PNG)
        # for i in contact_type:
        #     print(k, i)

def bed(approx_x, neg, pos, location_to_check):
    print(approx_x)
    global contact_type
    contact_type = []
    for i in location_to_check:
        bedding_surface = []
        for k in range(approx_x - neg, approx_x + pos):
            bedding_surface.append(rgb_im.getpixel((k, i)))
        print(bedding_surface)
        print(width, i, (m * (height - i) / ratio_px_pt) + c, Counter(bedding_surface).most_common(2))
        # print(Counter(bedding_surface).most_common(2)[1][1])
        if Counter(bedding_surface).most_common(1)[0][0] == (36, 31, 33):
            contact_type.append((m * (height - i) / ratio_px_pt) + c)
        elif Counter(bedding_surface).most_common(2)[0][0] == (255, 255, 255) and Counter(bedding_surface).most_common(2)[1][0] == (36, 31, 33) and  Counter(bedding_surface).most_common(2)[1][1] / Counter(bedding_surface).most_common(2)[0][1] > 0.8:
            print("WHITE / BLACK")
            contact_type.append((m * (height - i) / ratio_px_pt) + c)

    return contact_type


def group_runs(li, tolerance=1):
    out = []
    last = li[0]
    for x in li:
        if x-last > tolerance:
            yield out
            out = []
        out.append(x)
        last = x
    yield out
    # return out



# - Obtains all colors (1 pixel wide) at X location
# - Reduces colors to an amount equal to the user defined unique colors


def processing(defined_color_map):
    convert(pdf_name, resol)  # Convert pdf at the specified resolution
    load_image(fil_name)  # Load image and obtain necessary information
    ratio()  # Calculate ratio
    color_map  = []
    # defined_color_map = list(defined_color_map)
    print(defined_color_map)
    approx_x = 186 * ratio_px_pt

    processing_HZ_lines()

    print(green_text("\nProcessing color column. - PNG Mode"))
    print ("\nImage Loaded - Dimensions %s px X %s px @ %s dpi.\nPixel to Point ratio is: %.2f" % (width, height, resol, ratio_px_pt))


    # Obtain All Colors (1 Color/pixel) in the Lithological Identification
    for j in range(0, height):
        # print (j, rgb_im.getpixel((approx_x, j)))
        color_map.append(rgb_im.getpixel((approx_x, j)))

    print("No. of existing colors in Pixel ID %s column is: %s" % (bold_text(approx_x), bold_text(len(set(color_map)))))


    color_map_mode = Counter(color_map)  # counts the frequency of RGB Colors
    color_map_mode = (sorted(color_map_mode.items(), key=lambda g: g[1], reverse=True))  # Sorts ascending based on frequency

    # Reduces the colors the (X) amount of the max occurring colors
    # X is user defined
    # mode_counter = 0
    # for i, j in enumerate(color_map_mode):
    #     if mode_counter < defined_number_of_unique_colors:
    #         for k, color in enumerate(j):
    #             if k == 0 and color not in excluded_colors:
    #                 defined_color_map.append(color)
    #                 mode_counter += 1

    unique_color_map = defined_color_map  # Colors used in cleanup
    print("Looking up defined. A total of : %s" % bold_text(len(set(unique_color_map))))

    print(bold_text("User defined No. of Colors\n"))
    for i in unique_color_map:
        # actual_name, closest_name = get_colour_name(i)
        print("RGB: %s \t- Closest RGB colour name: %s" % (i, bold_text(get_colour_name(i)[1])))

    ## MOVE TO NEXT MODULE - IMAGE CLEANUP
    log_cleanup(color_map, unique_color_map)


'''
LOG CLEANUP
    # - Remove pixelated color making the log equivalent to the unique set defined
'''


def log_cleanup(color_map, unique_color_map):
    for i in range(1, len(color_map)):
        if color_map[i] not in unique_color_map:
            color_map[i] = color_map[i - 1]

    # for i, j in enumerate(color_map):
    #     print(m * ((len(color_map) - i) / ratio_px_pt) + c, j, get_colour_name(j)[1])

    # ## MOVE TO NEXT MODULE - REMOVE LINES
    remove_black_lines(color_map)

'''
REMOVE LINES

- Remove black lines (dividers)
- Splits the pixel thickness of the line and divides it into the upper and lower lithology
'''


def remove_black_lines(color_map):
    location = []
    for i in range(0, len(color_map) - 1):
        if color_map[i] == (36, 31, 33):
            if color_map[i] == color_map[i + 1]:
                location.append(i)
            else:
                location.append(i)
                for j, k in enumerate(location):
                    if k == 0:
                        color_map[k] = color_map[max(location) + 1]
                    elif j < (len(location) / 2):
                        color_map[k] = color_map[min(location) - 1]
                    else:
                        continue
                        # color_map[k] = color_map[max(location) + 1]
                location = []

    for h, k in enumerate(location):
        color_map[k] = color_map[min(location) - 1]

    color_map.pop()
    # print(color_map)

    global color_dict
    color_dict = {}
    for i, j in enumerate(color_map):
        # print("%.3f %s %s" %(m * ((len(color_map) - i) / ratio_px_pt) + c, j, get_colour_name(j)[1]))
        color_dict[m * ((len(color_map) - i) / ratio_px_pt) + c] = get_colour_name(j)[1]
    for k, v in color_dict.items():
        print(k, v)
    # exit(50)
    print(green_text("\nProcessed color column"))


def write_to_csv(h_lines, env, color, unique_loc):
    print(green_text("\nProcessing CSV Information"))
    h_lines = OrderedDict(sorted(h_lines.items(), key=lambda t: t[0]))
    env = OrderedDict(sorted(env.items(), key=lambda t: t[0]))
    print(dict(h_lines))
    color = OrderedDict(sorted(color.items(), key=lambda t: t[0]))
    list_of_dict = [env, ]
    list_of_dict_names = ["ENVIRONMENT", ]
    print(env)

    # print(h_lines)

    counter = 2
    for nam, dict_name in enumerate(list_of_dict):
        print("READING %s" % (list_of_dict_names[nam]))
        for k, v in h_lines.items():
            for k1, v1 in list(dict_name.items()):
                if v[0] < k1 < v[1]:
                    h_lines[k].append(v1)
                    del dict_name[k1]

        # print(dict_name)
        #
        if not dict_name:
            print(green_text("EVERYTHING in %s HAS BEEN MATCHED" % list_of_dict_names[nam]))
        else:
            print(red_text("The following has not been matched"))
            for k2, v2 in dict_name.items():
                print(k2, v2)
                print(red_text("$s - %s" % (k2, v2)))

        all_values = []
        for k in h_lines.keys():
            if  len(h_lines[k][counter:]) == 1:
                # print(green_text("MATCH %.3f - %s" % (k, h_lines[k])))
                continue
            elif len(h_lines[k][counter:]) > 1:
                print(red_text("PLEASE CHECK %.3f - %s" % (k, h_lines[k])))
                if h_lines[k][counter:][1] == h_lines[k][counter:][0]:
                    print(green_text("Considered as similar environment - %s" % h_lines[k][counter:][1]))
                    all_values.append(h_lines[k][counter:][1])
                    a = (h_lines[k][counter:][1])
                    h_lines[k][counter:][1] = a
                else:
                    print(h_lines[k][counter:])
                    all_values.append([' ? '.join(h_lines[k][counter:])])
                    a = ([' ? '.join(h_lines[k][counter:])])
                    h_lines[k][counter:] = a
            else:
                all_values.append(h_lines[k][counter:])

        print("EMPTY ENTRIES IN %s ARE BEING POPULATED AS \'UNKNOWN\'" % list_of_dict_names[nam])
        for k in h_lines.keys():
            if len(h_lines[k]) < counter + 1:
                h_lines[k].append("UNKNOWN")

        counter += 1

    # print(h_lines)
# def color_counter():
    from collections import Counter
    for k, v in h_lines.items():
        cat_val = []
        for k1, v1 in list(color.items()):
            if v[0] < k1 < v[1]:
                cat_val.append(v1)
        x = Counter(cat_val)
        cat_dict = (dict([((i, round(x[i] / len(cat_val) * 100.0))) for i in x])) # Change counter mode to %
        cat_dict = dict((litho_legend[key], value) for (key, value) in cat_dict.items()) # Change RGB to Lithology name
        val = (sorted(cat_dict.items(), key=lambda x: x[1], reverse=True)) # Value to return to Dictionary
        h_lines[k].append(val)

    # CLEANING BLANK SPACE FROM CSV
    for k, v in list(h_lines.items()):
        # print(len(v[3]), list(v[3][0])[0])
        # if len(v[3]) == 1 and list(v[3][0])[0] == 'Blank Space' and list(v[3][0])[1] == 99:
        if list(v[3][0])[0] == 'Blank Space' and list(v[3][0])[1] in [99, 100]:
            del h_lines[k]

    print(unique_loc)
    from collections import Counter
    for k, v in h_lines.items():
        cat_temp_val = []
        for k1 in unique_loc:
            k1 = (m * (height - (k1 / 2 )) / ratio_px_pt) + c
            if v[0] < k1 < v[1]:
                cat_temp_val.append(k1)
        x = len(cat_temp_val)
        # cat_temp_dict = (dict([((i, round(x[i] / len(cat_val) * 100.0))) for i in x]))
        # val = (sorted(cat_temp_dict.items(), key=lambda x: x[1], reverse = True))
        h_lines[k].append(x)

    # print(h_lines)
    # for k, v in h_lines.items():
    #     for i in np.arange(v[0], v[1], 1):
    #         # t = (bisect.bisect_left(list(color.keys()), i))
    #         maybe = color.get(i) or color[min(color.keys(), key=lambda k: abs(k-i))]
    #         if maybe in litho_legend:
    #             litho = litho_legend[maybe]
    #         else:
    #             litho = maybe
    #         print('%.4f %s %s' % (i, v[2:], litho))

    LAS_output = os.path.join(os.path.dirname(pdf_name), 'LAS_output.csv')
    with open(LAS_output,'w') as writecsv:
        writer = csv.writer(writecsv)
        writer.writerow(["Depth (m)", "Depositional Environment", "Lithology", "Biogenic", "Percentages"])
        for k, v in h_lines.items():
            for i in np.arange(v[0], v[1], 1):
                maybe = color.get(i) or color[min(color.keys(), key=lambda k: abs(k - i))]
                if maybe in litho_legend:
                    litho = litho_legend[maybe]
                else:
                    litho = maybe
                writer.writerow([i, v[2], litho, v[4], v[3]])
                print('%.4f \t%s \t%s \t%s \t%s' % (i, v[2], litho, v[4], v[3]))
    writecsv.close()

    layered_output = os.path.join(os.path.dirname(pdf_name), 'Layered_output.csv')
    with open(layered_output,'w') as writecsv:
        writer = csv.writer(writecsv)
        writer.writerow(["Depth To(m)", "Depth From (m)", "Depositional Environment", "Lithology (Mid Depth)", "Biogenic", "Percentages"])
        for k, v in h_lines.items():
            i = (v[0] + v[1]) / 2
            maybe = color.get(i) or color[min(color.keys(), key=lambda k: abs(k - i))]
            if maybe in litho_legend:
                litho = litho_legend[maybe]
            else:
                litho = maybe
            writer.writerow([v[0], v[1], v[2], litho, v[4], v[3]])
    writecsv.close()


'''
MAIN MODULE

- Returns total time and Error on user termination.
'''


if __name__ == "__main__":
    try:
        initial_processing()
        print ("Total Execution time: \033[1m%s\033[0m\n" % calc_timer_values(time.time() - abs_start))
    except KeyboardInterrupt:
        exit("TERMINATED BY USER")