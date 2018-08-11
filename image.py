# /////////////////////////////////////////////////////////////// #
# !python2.7
# -*- coding: utf-8 -*-
# Python Script initially created on 12/05/2018
# Compiled by Aly @ Grasselli's Geomechanics Group, UofT, 2018
# Created using PyCharm // Tested on Spyder
# Current Version 06 - Dated July 31, 2018
# /////////////////////////////////////////////////////////////// #

## This code was compiled based on the layout of d_66_I_94_B_16_Continuous_Core Log

# V01
#   - Initial release

# V02
#   - PDF conversion is completely housed within the script.
#   - Code optimization {Split into different modules}.
#   - Modules run for different pixel columns as defined.
#   - Identifies depositional bedding type.

# V03
#   - Adjust scale based on dpi.
#   - Code optimization {Algorithm changed}.
#   - Changed colors in terminal outputs.
#   - PDF split into MediaBOX to have a higher resolution image during template matching.
#   - Template matching functional.

# V04
#   - Write to Sediment and Environment to CSV.
#   - Code optimization {Algorithm changed}.

# V05
#   - Added the colour code to the visual output on python terminal.
#   - Scaling template from 90% to 110% (90, 100, 110) to ook for possible matches
#   - Fixed issue with different size (length) logs

# V06
#   - Vision changed to using OCRs


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

# Locations of items to look for. Format {"WHAT" : [X coordinate from left of log, Y coordinate from top of log]}
# locations = {'Name:' : [475, 734], 'Well Location:' : [100, 748] , 'Fm/Strat. Unit:' : [308, 734], 'Date:' : [469, 706]}
locations = {'Name:' : [475, 56], 'Well Location:' : [100, 42] , 'Fm/Strat. Unit:' : [308, 56], 'Date:' : [469, 84]}

# Abbreviation of the Dep. Env. / Sedimentary Facies
# Will display an error if the text recognised in the Env. column is not in this list.
env_list = ['H', 'O', 'OTD', 'OTP', 'T. Lag', 'Ramp', 'Distal Ramp', 'T', 'Temp', 'OT', 'LS', 'Turb', 'Temps']

# Resolutions
h_resol = 600
resol = 300

## DICTIONARY
litho_legend = {"skyblue": "Laminated Bedded Resedimented Bioclasts", "sandybrown": "Bituminous F-C Siltstone", "tan": "Bituminous F-M Siltstone", "khaki": "Sandy F-C Siltstone to Silty VF Sandstone", "darkseagreen": "Phosphatic - Bituminous Sandy Siltstone to Breccia", "plum": "Calcareous - Calcispheric Dolosiltstone"}
excluded_colors = [(255, 255, 255), (36, 31, 33), (94, 91, 92), (138, 136, 137), (197, 195, 196), (187, 233, 250), (26, 69, 87)]  # exclusion colors from mapping [(White), (Black), (Dim Grey), (Grey), (Silver), (paleturquoise), (darkslategray)]



'''
TIMER FUNCTION
'''


def calc_timer_values(end_time):
    minutes, sec = divmod(end_time, 60)
    if end_time < 60:
        return "\033[1m%.2f seconds\033[0m" % end_time
    else:
        return "\033[1m%d minutes and %d seconds\033[0m." % (minutes, sec)

abs_start = time.time()

def red_text(val):
    tex = "\033[1;31m%s\033[0m" % val
    return tex

def green_text(val):
    tex = "\033[1;92m%s\033[0m" % val
    return tex

def bold_text(val):
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
    # - If not found returns nearest color name in spectrum
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
# Default PDF reader usually return  unicode string.
# Convert the given unicode string to a bytestring, using the standard encoding, unless it's already a bytestring.
'''


def to_bytestring (s, enc='utf-8'):
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)

# Open a PDF file.
# pdf_name = '/home/aly/Desktop/log2/d_66/d_66_I_94_B_16_Continuous_Core.pdf'
pdf_name = '/home/aly/Desktop/log2/talisman/Talisman c-65-F_Page 1.pdf'
# pdf_name = 'C:/Users/alica/Desktop/log2/d_66/d_66_I_94_B_16_Continuous_Core.pdf'
# pdf_name = 'C:/Users/alica/Desktop/log2/talisman/Talisman_c-65-F_Page_1.pdf'

'''
GLOBAL OPENING OF FILE
'''

fp = open(pdf_name, 'rb')

def update_page_text_hash (h, lt_obj, pct=0.2):
    """Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""
    x0 = lt_obj.bbox[1]
    x1 = lt_obj.bbox[3]
    key_found = False
    for k, v in h.items():
        hash_x0 = k[1]
        if x0 >= (hash_x0 * (1.0-pct)) and (hash_x0 * (1.0+pct)) >= x0:
            hash_x1 = k[0]
            if x1 >= (hash_x1 * (1.0-pct)) and (hash_x1 * (1.0+pct)) >= x1:
                # the text inside this LT* object was positioned at the same
                # width as a prior series of text, so it belongs together
                key_found = True
                v.append(to_bytestring(lt_obj.get_text()))
                h[k] = v
    if not key_found:
        # the text, based on width, is a new series,
        # so it gets its own series (entry in the hash)
        h[(x0,x1)] = [to_bytestring(lt_obj.get_text())]
    return h

'''
PROCESS // PARSE ALL PDF

- Loops over ALL the identified elements in the PDF
- Obtains their bounding box
'''


def parse_obj(lt_objs, y_loc):
    coord, corel, depths = [], {}, {}
    '''
    PROCESS // PARSE DEPTH ALL DATA
    '''
    # bbox(bounding box) attribute, which is a four - part  tuple of the object's page position: (x0, y0, x1, y1)
    for obj in lt_objs:
        # if it's a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            # print("%6d, %6d, %6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3], obj.get_text().replace('\n', '_')))  # Print all OCR Matches and the bounding box locations.
            coord.append([obj.bbox[0], obj.bbox[1]])  # List of all X/Y of bounding boxes.
            corel[obj.get_text().replace('\n', '_')] = [obj.bbox[0], obj.bbox[1]]  # Dictionary of {TEXT : [X , Y]}
        # if it's a container, recurse. That is, LTFigure objects are containers for other LT* objects, so recurse through the children
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
                try:
                    depths[int(obj.bbox[1])] = int(obj.get_text().replace('\n', ''))
                except ValueError:
                    print(red_text("Error in Depth Column\nPossible text deteceted:\t %s" % obj.get_text().replace('\n', '_')))
                    # exit("Status 10 - Text identified in the Depth Column. Please change value of y_loc.")


    # Sort by location in the column
    # Seperate the OCR depth from the point location
    depths = OrderedDict(sorted(depths.items(), key=lambda t: t[0]))
    a, b = [], []
    for key in depths:
        # print("%s: %s" % (key, depths[key]))  # DISPLAY the OCR of the text sequence {Pt. : OCR Depth value}
        a.append(depths[key])
        b.append(key)

    # Load module to check information in depth column
    list_a = check_depth_column('Depths Values', a)
    list_b = check_depth_column('Pixel Location', b)

    # Improvement - How can this difference be quantitative? Standard Deviation?
    # import statistics
    # print(statistics.stdev([(x*1.0) / y for x,y in zip(list_a, list_b)]))

    # Equation of linear correlation between
    # OCR depth [a] & point location [b]
    y, x = [a[0], a[-1]], [b[0], b[-1]]
    coeff(x, y)

    print(green_text("\nProcessed Depth Column - OCR Mode.\nCoeff : %.3f x + %.3f.\n" % (m, c)))

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
    texts = {}
    for obj in lt_objs:
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            if int(obj.bbox[0]) in range(524, 535) and int(obj.bbox[1]) < y_loc:
                # text, location = "%.3f, %s" % (m * obj.bbox[1] + c, obj.get_text().replace('\n', '_'))
                # print("%.3f, %s" % (m * obj.bbox[1] + c, obj.get_text().replace('\n', '_')))
                # d = m * obj.bbox[1] + c
                texts[m * obj.bbox[1] + c] = obj.get_text().replace('\n', '_')
                # print(obj.bbox[1], obj.bbox[1] / ratio, obj.get_text().replace('\n', '_'))

    # for k,v in texts.items():
    #     print(k,v)

    split_texts, deleted_keys = {}, []
    print(bold_text("Validating OCR in Environment Column\n"))
    for key, v in list(texts.items()): # In Python 3.x, use list(data.items()). In Python 2.7+ use data.items().
        if v.count("_") > 1 and v not in ["Distal_Ramp_"]:
            print("Manual \'Enter\' detected - %s" % v)
            underscore_list = v.split("_")  # Split on '_'
            underscore_list.pop()  # Remove the last '_'
            del texts[key]  # Delete that key from the dictionary
            # deleted_keys.append(key)
            # Adjust X based on the number of manual enters within the text box.
            for loc, i in enumerate(underscore_list):
                delta = (len(underscore_list) - 1 - loc) * (m * (16.3))
                texts[key + delta] = i
        else:
            if v.endswith('_'):
                v = v[:-1]
                texts[key] = v.replace('_', ' ')
            # else:
            #     texts[key] = v.replace('_', ' ')


    comb = permutations(env_list, 2)
    env_matches = {}
    for k,v in texts.items():
        if v in env_list:
            # print("Match %0.3f - %s" % (k, v))
            env_matches[k] = v
        elif '/' in v:
            print('Possibly Dual Environment \t %0.3f - %s' % (k, v))
            a = v.split('/')
            print(red_text('Found Possible matches %s') % ' and '.join(a))
            for i in a:
                if i in env_list:
                    # print("SUB - Match %0.3f - %s" % (k, i))
                    env_matches[k] = i
                elif i == '':
                    # print("Empty String")
                    continue
                else:
                    print(bold_text('PLEASE CHECK! %s') % red_text(i))
                    for k in list(comb):
                        n = ''.join(k)
                        if i == n:
                            print(red_text('Found Possible matches %s') % ' and '.join(k))
                            # env_matches[k] = v

        else:
            print('UNKNOWN %0.3f - %s' % (k, v))
        # print(k,v)

    # print(env_matches)  # DISPLAY the entire environment matches {DEPTH : VALUE}
    print(green_text("\nProcessed Environments - OCR Mode\n"))


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

## Improvement
# 1) Make the match not on X/Y but on the next X in the line (Same Y Value).
# 2) Does not work if there is a  manual enter by the user in the log.


def log_info(coord, corel):
    coord_myarray = np.asarray(coord)  # convert nested list to numpy array
    for k, v in locations.items():
        v[1] = tot_len - v[1]  # Get the depth from the top.
        alpha = coord_myarray[spatial.KDTree(coord_myarray).query(v)[1]]  # Lookup nearest point to predefined location
        for k1, v1 in corel.items():
            if v1 == list(alpha):
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
# How can this difference be quantitative - Standard Deviation?
# What constituents bad//good.

def check_depth_column(name, list_values):
    if name == 'Depth Values':
        # list_values = list(reversed(list_values))
        for x, i in enumerate(list_values):
            if x < len(list_values) - 1 :
                    if list_values[x] < list_values[x + 1]:
                        print("Check the depth column for Typos")
                        # exit(11)
    unique_values = len(set(np.diff(list_values)))
    diff = abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values))))
    if len(set(np.diff(list_values))) == 1 or abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values)))) < 2:
         print(green_text("\n%s in the DEPTH COLUMN CHECKED" % name))
    # elif abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values)))) < 2:
    #     print("MINOR Error in scale of %s, off by %s units" % (name, diff))
    else:
        print(red_text("Status 12 - MINOR Error in scale of %s, off by %s units\nValues are %s" % (name, diff, np.diff(list_values))))
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
        parse_obj(layout._objs, tot_len - 190)

        # Convert PDF to process lithology column and obtain Pt./Pixel Ratio
        processing(len(litho_legend))

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
    print ("Image Loaded - Dimensions %s px X %s px @ %s dpi.\nPixel to Point ratio is: %.2f" % (temp_w, temp_h, h_resol, ratio_px_pt))

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

# - Obtains all colors (1 pixel wide) at X location
# - Reduces colors to an amount equal to the user defined unique colors


def processing(defined_number_of_unique_colors):
    print(green_text("\nProcessing color column. - PNG Mode"))
    convert(pdf_name, resol)  # Convert pdf at the specified resolution
    load_image(fil_name)  # Load image and obtain necessary information
    ratio()  # Calculate ratio
    color_map, defined_color_map  = [], []
    approx_x = 186 * ratio_px_pt
    print ("Image Loaded - Dimensions %s px X %s px @ %s dpi.\nPixel to Point ratio is: %.2f" % (width, height, resol, ratio_px_pt))

    # Obtain All Colors (1 Color/pixel) in the Lithological Identification
    for j in range(0, height):
        # print (j, rgb_im.getpixel((approx_x, j)))
        color_map.append(rgb_im.getpixel((approx_x, j)))

    print("No. of existing colors in Pixel ID %s column is: %s" % (bold_text(approx_x), bold_text(len(set(color_map)))))


    color_map_mode = Counter(color_map)  # counts the frequency of RGB Colors
    color_map_mode = (sorted(color_map_mode.items(), key=lambda g: g[1], reverse=True))  # Sorts ascending based on frequency

    # Reduces the colors the (X) amount of the max occurring colors
    # X is user defined
    mode_counter = 0
    for i, j in enumerate(color_map_mode):
        if mode_counter < defined_number_of_unique_colors:
            for k, color in enumerate(j):
                if k == 0 and color not in excluded_colors:
                    defined_color_map.append(color)
                    mode_counter += 1

    unique_color_map = defined_color_map + excluded_colors  # Colors used in cleanup
    print("Looking up defined and excluded colors. A total of : %s" % bold_text(len(set(unique_color_map))))

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
                        color_map[k] = color_map[max(location) + 1]
                location = []

    for h, k in enumerate(location):
        color_map[k] = color_map[min(location) - 1]

    color_map.pop()

    # for i, j in enumerate(color_map):
    #     print("%.3f %s %s" %(m * ((len(color_map) - i) / ratio_px_pt) + c, j, get_colour_name(j)[1]))


'''
MAIN MODULE

- Returns total time and Error on user termination.
'''


if __name__ == "__main__":
    try:
        initial_processing()
        # cropping_pdf()
        # Load processing module using Lithological Identification parameters
        # processing(len(litho_legend))
        print ("Total Execution time: \033[1m%s\033[0m\n" % calc_timer_values(time.time() - abs_start))
    except KeyboardInterrupt:
        exit("TERMINATED BY USER")