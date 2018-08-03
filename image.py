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
import pdfminer
import time
import cv2
import numpy as np
from scipy import spatial
from collections import OrderedDict

# Locations of items to look for. Format {"WHAT" : [X coordinate from left of log, Y coordinate from top of log]}
# locations = {'Name:' : [475, 734], 'Well Location:' : [100, 748] , 'Fm/Strat. Unit:' : [308, 734], 'Date:' : [469, 706]}
locations = {'Name:' : [475, 56], 'Well Location:' : [100, 42] , 'Fm/Strat. Unit:' : [308, 56], 'Date:' : [469, 84]}

# Abbreviation of the Dep. Env. / Sedimentary Facies
# Will display an error if the text recognised in the Env. column is not in this list.
env_list = ['H', 'O', 'OTD', 'OTP', 'T. Lag', 'Ramp', 'Distal Ramp', 'T', 'Temp', 'OT', 'LS', 'Turb']


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

'''
INITIALIZING PDF FILE FOR DATA EXTRACTION

- SCRIPT OBTAINED FROM https://stackoverflow.com/questions/22898145/how-to-extract-text-and-text-coordinates-from-a-pdf-file
'''

# Open a PDF file.
# fp = open('/home/aly/Desktop/Talisman_c-65-F_Page 1.pdf', 'rb')
fp = open('/home/aly/Desktop/d_66_I_94_B_16_Continuous_Core.pdf', 'rb')

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
            print("%6d, %6d, %6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3], obj.get_text().replace('\n', '_')))  # Print all OCR Matches and the bounding box locations.
            coord.append([obj.bbox[0], obj.bbox[1]])  # List of all X/Y of bounding boxes.
            corel[obj.get_text().replace('\n', '_')] = [obj.bbox[0], obj.bbox[1]]  # Dictionary of {TEXT : [X , Y]}
        # if it's a container, recurse. That is, LTFigure objects are containers for other LT* objects, so recurse through the children
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs)

    # Run the module
    log_info(coord, corel)

    '''
    PROCESS // PARSE DEPTH COLUMN
    
    - Lookup depth column (X = 40 to 60 & Y = 180 points from top of page).
    - Identifies presence of integers to establish scale.
    - Returns error is anything apart from integers is encounterd.
    '''
    for obj in lt_objs:
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            if int(obj.bbox[0]) in range(40,60) and int(obj.bbox[1]) < y_loc:
                try:
                    depths[int(obj.bbox[1])] = int(obj.get_text().replace('\n', ''))
                except ValueError:
                    print("\033[1;31m Error in Depth Column - %s\033[0m" % obj.get_text().replace('\n', '_'))
                    # exit("Status 10 - Text identified in the Depth Column. Please change value of y_loc.")


    # Sort by location in the column
    # Seperate the OCR depth from the point location
    depths = OrderedDict(sorted(depths.items(), key=lambda t: t[0]))
    a, b = [], []
    for key in depths:
        print("%s: %s" % (key, depths[key]))
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
    m, c = np.polyfit(x, y, 1)
    print("Coeff : %.3f x + %.3f" % (m, c))

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
                print("%.3f, %s" % (m * obj.bbox[1] + c, obj.get_text().replace('\n', '_')))
                # d = m * obj.bbox[1] + c
                texts[m * obj.bbox[1] + c] = obj.get_text().replace('\n', '_')
                # print(obj.bbox[1], obj.bbox[1] / ratio, obj.get_text().replace('\n', '_'))

    # for k,v in texts.items():
    #     print(k,v)

    split_texts, deleted_keys = {}, []
    for key, v in list(texts.items()): # In Python 3.x, use list(data.items()). In Python 2.7+ use data.items().
        if v.count("_") > 1 and v not in ["Distal_Ramp_"]:
            print("Needs to be split - %s" % v)
            underscore_list = v.split("_")  # Split on '_'
            underscore_list.pop()  # Remove the last '_'
            del texts[key]  # Delete that key from teh dictionary
            # deleted_keys.append(key)
            # Adjust X based on the number of manual enters within the text box.
            for loc, i in enumerate(underscore_list):
                delta = (len(underscore_list) - 1 - loc) * (m * (16.3))
                texts[key + delta] = i
        else:
            if v.endswith('_'):
                v = v[:-1]
                texts[key] = v.replace('_', ' ')
            else:
                texts[key] = v.replace('_', ' ')

    for k,v in texts.items():
        if v in env_list:
            print("Match %0.3f - %s" % (k, v))
        elif '/' in v:
            print('Two ENV? %0.3f - %s' % (k, v))
            a = v.split('/')
            print(a)
            for i in a:
                if i in env_list:
                    print("SUB - Match %0.3f - %s" % (k, i))
                else:
                    print('\033[1;31m PLEASE CHECK! %s \033[0m' % i)
        else:
            print('UNKNOWN %0.3f - %s' % (k, v))
        # print(k,v)



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
    coord_myarray = np.asarray(coord) # convert nested list to numpy array
    for k, v in locations.items():
        v[1] = tot_len - v[1]
        alpha = coord_myarray[spatial.KDTree(coord_myarray).query(v)[1]] # Lookup nearest point to predefined location
        for k1, v1 in corel.items():
            if v1 == list(alpha):
                print(k, '\t', k1)

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
    if len(set(np.diff(list_values))) == 1:
         print("%s in the DEPTH COLUMN CHECKED" % name)
    elif abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values)))) < 2:
        print("MINOR Error in scale of %s, off by %s units" % (name, diff))
    else:
        print("\033[1;31m Status 12 - MINOR Error in scale of %s, off by %s units\nValues are %s \033[0m" % (name, diff, np.diff(list_values)))
        # exit("Status 12 - MINOR Error in scale of %s, off by %s units\nValues are %s" % (name, diff, np.diff(list_values)))
    return np.diff(list_values)


'''
INITIALIZING MAIN MODULE FOR EXECUTION

- Open PDF and obtain file extents. Mainly "y_top" that will be used for further processing.
- Size of MEDIABOX returned in points.
'''


def initial_processing():
    global tot_len
    # loop over all pages in the document
    for page in PDFPage.create_pages(document):

        # read the media box that is the page size as list of 4 integers x0 y0 x1 y1
        print(page.mediabox)
        _, _, _, tot_len = page.mediabox

        # read the page into a layout object
        # receive the LTPage object for this page
        interpreter.process_page(page)
        # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
        layout = device.get_result()

        # load module to parse every object encountered in the PDF
        parse_obj(layout._objs, tot_len - 190)


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