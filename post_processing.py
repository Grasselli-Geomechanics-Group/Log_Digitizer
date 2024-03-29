# # /////////////////////////////////////////////////////////////// #
# # !python3.6
# # -*- coding: utf-8 -*-
# # Python Script initially created on 18/11/2018
# # Compiled by Aly @ Grasselli's Geomechanics Group, UofT, 2018
# # Created using PyCharm // Tested on Spyder
# # Current Version 01 - Dated November 18, 2018
# # /////////////////////////////////////////////////////////////// #
#
# # Code written to convert modified CSV files to LAS
#
# from pdfminer.pdfparser import PDFParser
# from pdfminer.pdfdocument import PDFDocument
# from pdfminer.pdfpage import PDFPage
# from pdfminer.pdfpage import PDFTextExtractionNotAllowed
# from pdfminer.pdfinterp import PDFResourceManager
# from pdfminer.pdfinterp import PDFPageInterpreter
# from pdfminer.pdfdevice import PDFDevice
# from pdfminer.layout import LAParams
# from pdfminer.converter import PDFPageAggregator
# from pdfminer.pdfinterp import resolve1
# from PyPDF2 import PdfFileWriter, PdfFileReader
# from scipy import spatial
# from collections import OrderedDict
# from operator import itemgetter
# from itertools import permutations
# from scipy.spatial import distance
# from PIL import Image
# import PIL.ImageOps
# from collections import Counter
# import numpy as np
# import pdfminer
# import time
# import os
# import fnmatch
# import imutils
# import cv2
# import random
# import webcolors
# import csv
# import math
# import sys
# import argparse
# import platform
#
# # START OF EXECUTION
# abs_start = time.time()
#
# # Locations of items to look for. Format {"WHAT" : [X coordinate from left of log, Y coordinate from top of log]}
# locations = {'Name:': [475, 56], 'Well Location:': [100, 42], 'Fm/Strat. Unit:': [308, 56], 'Date:': [469, 84]}
#
# # Abbreviation of the Dep. Env. / Sedimentary Facies
# # Will display an error if the text recognised in the Env. column is not in this list.
# env_list = ['H', 'O', 'OTD', 'OTP', 'T. Lag', 'Ramp', 'Distal Ramp', 'T', 'Temp', 'OT', 'LS', 'Turb', 'Temps', 'Seismite', 'Fluidized Flow', 'Hemipelagite', 'Tempestites', 'Tempestite']
#
# # Resolutions
# h_resol = 600
# resol = 300
#
# # DICTIONARY
# litho_legend = {"skyblue": "Laminated Bedded Resedimented Bioclasts", "sandybrown": "Bituminous F-C Siltstone", "tan": "Bituminous F-M Siltstone", "khaki": "Sandy F-C Siltstone to Silty VF Sandstone", "darkseagreen": "Phosphatic - Bituminous Sandy Siltstone to Breccia", "plum": "Calcareous - Calcispheric Dolosiltstone", "darkkhaki": "Bituminous F-M Siltstone", "goldenrod": "Bituminous F-C Siltstone", "white": "Blank Space", "black": "Hz Line"}
# # excluded_colors = [(255, 255, 255), (36, 31, 33), (94, 91, 92), (138, 136, 137), (197, 195, 196), (187, 233, 250), (26, 69, 87)]  # exclusion colors from mapping [(White), (Black), (Dim Grey), (Grey), (Silver), (paleturquoise), (darkslategray)]
# # defined_color_map = [(201, 163, 127), (250, 166, 76), (122, 176, 222), (255, 245, 135), (199, 161, 201), (156, 212, 173), (255, 255, 255), (36, 31, 33), (35, 31, 32)]  # Defined colors [(tan), (sandybrown), (skyblue), (khaki), (plum), (darksgreen)]
# defined_color_map = [(210, 180, 140), (244, 164, 96), (135, 206, 235), (240, 230, 140), (143, 188, 143), (221, 160, 221), (218, 165, 32), (189, 183, 107), (255, 255, 255), (0, 0, 0)]
#
#
# '''
# GLOBAL OPENING OF FILE
#
# - Insert File name to open
# - Load file
# '''
#
#
# def open_file(f_name):
#     global pdf_name, fp
#     pdf_name = f_name
#     fp = open(pdf_name, 'rb')
#     initial_processing()
#
# '''
# TIMER FUNCTION
# '''
#
#
# def calc_timer_values(end_time):
#     minutes, sec = divmod(end_time, 60)
#     if end_time < 60:
#         return bold_text("%.2f seconds" % end_time)
#     else:
#         return bold_text("%d minutes and %d seconds" % (minutes, sec))
#
#
# '''
# FORMATTING OPTIONS
#
# - TEXT COLORS
# '''
#
#
# def red_text(val):  # RED Bold text
#     tex = "\033[1;31m%s\033[0m" % val
#     return tex
#
#
# def green_text(val):  # GREEN Bold text
#     tex = "\033[1;92m%s\033[0m" % val
#     return tex
#
#
# def bold_text(val):  # Bold text
#     tex = "\033[1m%s\033[0m" % val
#     return tex
#
#
# '''
# DEFINE THE RGB SPECTRUM FOR VISUAL APPEAL
# '''
#
#
# def closest_colour(requested_colour):
#     min_colours = {}
#     for key, name in webcolors.css3_hex_to_names.items():
#         r_c, g_c, b_c = webcolors.hex_to_rgb(key)
#         rd = (r_c - requested_colour[0]) ** 2
#         gd = (g_c - requested_colour[1]) ** 2
#         bd = (b_c - requested_colour[2]) ** 2
#         min_colours[(rd + gd + bd)] = name
#     return min_colours[min(min_colours.keys())]
#
#
# '''
# GET COLOR NAME BASED ON RGB SPECTRUM
#
# - If not found returns nearest color name in spectrum
# '''
#
#
# def get_colour_name(requested_colour):
#     try:
#         closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
#     except ValueError:
#         closest_name = closest_colour(requested_colour)
#         actual_name = None
#     return actual_name, closest_name
#
#
# '''
# CONVERT BYTES TO STRING
#
# - Default PDF reader usually return  unicode string.
# - Convert the given unicode string to a bytestring, using the standard encoding, unless it's already a bytestring.
# '''
#
#
# def to_bytestring(s, enc='utf-8'):
#     if s:
#         if isinstance(s, str):
#             return s
#         else:
#             return s.encode(enc)
#
#
# '''
# PROCESS // PARSE ALL PDF
#
# - Loops over ALL the identified elements in the PDF
# - Obtains their bounding box
# '''
#
#
# def parse_obj(lt_objs):
#     coord, corel, depths = [], {}, {}
#     y_loc = tot_len - 190
#
#     '''
#     PROCESS // PARSE DEPTH ALL DATA
#
#     - Y is captured as the mid-height of the bounding box.
#     '''
#
#     # bbox(bounding box) attribute of a textbox, is a four-part tuple of the object's page position: (x0, y0, x1, y1)
#     # position is returned in terms of Pt. units. Where 0 is the bottom-right of the page.
#     for obj in lt_objs:
#         # if it is a textbox, print text and location
#         if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
#             y_mid_height = (obj.bbox[1] + obj.bbox[3]) / 2
#             # DISPLAY All Text Extraction Matches on the page.
#             # print("%6d, %6d, %6d, %6d, => %6d - %6d => dx=%6d dy=%6d - %s" % (obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3], obj.bbox[0], y_mid_height, obj.bbox[2] - obj.bbox[0], obj.bbox[3] - obj.bbox[1],  obj.get_text().replace('\n','_')))  # Print all Text Extraction Matches and the bounding box locations.
#             coord.append([obj.bbox[0], y_mid_height])  # List of all X/Y of bounding boxes. Y is mid/height.
#             corel[obj.get_text().replace('\n', '_')] = [obj.bbox[0], y_mid_height]  # Dictionary of {TEXT : [X , Y]}
#         # if it is a container, recurse. That is, LTFigure objects are containers for other LT* objects, so recurse through the children
#         elif isinstance(obj, pdfminer.layout.LTFigure):
#             parse_obj(obj._objs)
#
#     print(green_text("PDF Text Extraction COMPLETED. \n"))
#
#     # Run the module to obtain any possible information of the log.
#     log_info(coord, corel)
#
#     '''
#     PROCESS // PARSE DEPTH COLUMN
#
#     - Lookup depth column (X = 40 to 60 & Y = y_top from top of page).
#     - Identifies presence of integers to establish scale.
#     - Returns error if anything apart from integers is encountered.
#     '''
#
#     for obj in lt_objs:
#         if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
#             if int(obj.bbox[0]) in range(40, 60) and int(obj.bbox[1]) < y_loc:
#                 # Checks for integers, produces error and continues if non-integer encountered
#                 try:
#                     y_mid_height = (obj.bbox[1] + obj.bbox[3]) / 2
#                     depths[int(y_mid_height)] = int(obj.get_text().replace('\n', ''))
#                 except ValueError:
#                     print(red_text("Error in Depth Column\nPossible text detected:\t %s" % obj.get_text().replace('\n', '_')))
#
#     # Sort by location in the column
#     # Separate the Text Extraction depth from the point location
#     depths = OrderedDict(sorted(depths.items(), key=lambda t: t[0]))
#     a, b = [], []
#
#     for key in depths:
#         a.append(depths[key])
#         b.append(key)
#
#     # Load module to check information in depth column
#     check_depth_column('Depths Values', a)
#     check_depth_column('Pt. Location', b)
#
#     # Improvement - How can this difference be quantitative? Standard Deviation?
#     # import statistics
#     # print(statistics.stdev([(x*1.0) / y for x,y in zip(list_a, list_b)]))
#
#     # Equation of linear correlation between Text Extraction depth [a] & Pt. location [b]
#     # between second and second last to avoid movement of last depth avoiding extension of page
#     # Identified and overcomes depths at extents of log (Lily a-9-J).
#     y, x = [a[1], a[-2]], [b[1], b[-2]]
#     coeff(x, y)
#
#     # DISPLAY the entire depth column matches {DEPTH : VALUE}
#     print(green_text("\nProcessed Depth Column - Text Extraction Mode.\nCoeff : %.3f x + %.3f.\n" % (m, c)))
#     print("Pt. : Text Extraction Depth value")
#     for key in depths:
#         print("%s Pt. : %s meters" % (key, bold_text(depths[key])))  # DISPLAY the Text Extraction of the text sequence {Pt. : Text Extraction Depth value}
#     # print(green_text("\nProcessed Depth Column - Text Extraction Mode.\nCoeff : %s x + %s.\n" % (m, c)))
#
#     '''
#     PROCESS // PARSE ENVIRONMENT COLUMN
#
#     - Lookup depth column (X = 524 to 535 & Y = y_top from top of page).
#     - Identifies presence of information in the column.
#     - If text has more than one manual enter, split on the '_'. And in any case remove the last '_'
#     - In that case, adjust the X location to match the start of a new line. dy calculated as font size differs across logs.
#     - After parsing the data:
#         - If has "/" then two environments.
#         - Lookup environments in the predefined dictionary.
#         - In case of two environments; will check both.
#     - Will show error if it can not understand the text OR the "/" is at the start or end of the string.
#     '''
#
#     ''' CONSIDER THIS IN A POOL'''
#
#     texts, dys = {}, []
#     for obj in lt_objs:
#         if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
#             if int(obj.bbox[0]) in range(520, 535) and int(obj.bbox[1]) < y_loc:
#                 # text, location = "%.3f, %s" % (m * obj.bbox[1] + c, obj.get_text().replace('\n', '_'))
#                 # print("%.3f, %s" % (m * obj.bbox[1] + c, obj.get_text().replace('\n', '_')))
#                 # print(m * obj.bbox[1] + c, m * obj.bbox[3] + c)
#                 y_mid_height = (obj.bbox[1] + obj.bbox[3]) / 2
#                 texts[m * y_mid_height + c] = obj.get_text().replace('\n', '_')
#                 if obj.get_text().replace('\n', '_').count('_') == 1:
#                     dys.append(abs(obj.bbox[1] - obj.bbox[3]))
#                     # print(abs(obj.bbox[1] - obj.bbox[3]), obj.get_text().replace('\n', '_'))
#                 # print(obj.bbox[1], obj.bbox[1] / ratio, obj.get_text().replace('\n', '_'))
#
#     # for k,v in texts.items():
#     #     print(k,v)
#     dy = (sum(dys) / len(dys))
#
#     print(bold_text("\nValidating Text Extraction in Environment Column\n"))
#     if dys:
#         print(bold_text("Manual 'Enter' detected. Defined as %.2f Pt.\n" % dy))
#     for key, v in list(texts.items()):
#         if v.count("_") > 1 and v not in ["Distal_Ramp_"]:
#             print("Manual \'Enter\' detected - %s" % v)
#             underscore_list = v.split("_")  # Split on '_'
#             underscore_list.pop()  # Remove the last '_'
#             del texts[key]  # Delete that key from the dictionary
#             # Adjust Y location based on the number of manual enters within the text box.
#             # print(m * dy)
#             for loc, i in enumerate(underscore_list):
#                 delta = (m * (dy * ((len(underscore_list) - loc) - (len(underscore_list) / 2) - 0.5)))
#                 # print(key, delta, key + delta, loc, i)
#                 texts[key + delta] = i
#         else:
#             if v.endswith('_'):
#                 v = v[:-1]
#                 texts[key] = v.replace('_', ' ')
#     # exit(50)
#     # create a list of all possible permutations of the environment, based on sets of 2.
#     comb = permutations(env_list, 2)
#     global env_matches
#     env_matches = {}
#     for k, v in texts.items():
#         if v in env_list:
#             # DISPLAYS ALL MATCHES
#             # print("Match %0.3f - %s" % (k, v))
#             env_matches[k] = v
#         elif '/' in v:
#             print('Possibly Dual Environment \t %0.3f - %s' % (k, v))
#             a = v.split('/')
#             print(green_text('Found Possible matches %s') % ' and '.join(a))
#             env_matches[k] = ' / '.join(a)
#             for i in a:
#                 if i in env_list or i == '':  # If only one string found, or blank space encountered, continue.
#                     continue
#                 else:
#                     print(bold_text('PLEASE CHECK! %s') % red_text(i))  # Else check possible matches in the permutations list.
#                     for b in list(comb):
#                         n = ''.join(b)
#                         if i == n:
#                             print(red_text('Found Possible matches %s') % ' and '.join(b))
#                             env_matches[k] = ' / '.join(b)
#         else:
#             print(red_text('UNKNOWN %0.3f - %s' % (k, v)))
#
#     env_matches = OrderedDict(sorted(env_matches.items()))
#     # DISPLAY the entire environment matches {DEPTH : VALUE}
#     print(green_text("\nProcessed Environments - Text Extraction Mode\n"))
#     print('Depth (m) : Environment')
#     for key in env_matches:
#         print("%.3f : %s" % (key, bold_text(env_matches[key])))
#
#
# '''
# LOG INFO
#
# - Obtains important information from the log.
# - Locations are returned based on the "locations' dictionary
# '''
#
# # Possible Improvement
# # 1) Make the match not on X/Y but on the next X in the line (Same Y Value).
# # 2) Does not work if there is a  manual enter by the user in the log.
#
#
# def log_info(coord, corel):
#     coord_myarray = np.asarray(coord)  # convert nested list to numpy array
#     for k, v in locations.items():  # Load locations of identified text
#         v[1] = tot_len - v[1]  # Get the depth from the top.
#         alpha = coord_myarray[spatial.KDTree(coord_myarray).query(v)[1]]  # Lookup nearest point to predefined location
#         for k1, v1 in corel.items():  # Load the correlation dictionary
#             if v1 == list(alpha):  # Lookup position matches and return matching information.
#                 if k1.count("_") > 1:
#                     print(bold_text(k), '\t', k1.split('_')[0])
#                 else:
#                     print(bold_text(k), '\t', k1.replace('_', ''))
#
#
# '''
# DEPTH COLUMN - VALIDATION
#
# - Checks depth column for
# 1) Value of depth (makes sure it is an integer)
# 2) Ensures that they are in descending order
# 3) Check the ratio (i.e. difference between the depths and their location on the log)
# '''
#
# # Improvement
# # 1) Make the comparison of the ratio by d_depth over d_point.
# # How can this difference be quantitative - Standard Deviation / COV?
# # What constituents bad//good.
#
#
# def check_depth_column(name, list_values):
#     if name == 'Depth Values':
#         for x, i in enumerate(list_values):
#             if x < len(list_values) - 1:
#                     if list_values[x] < list_values[x + 1]:
#                         print("Check the depth values for Typos")
#
#     if len(set(np.diff(list_values))) == 1 or abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values)))) < 2:
#         print(green_text("\n%s in the Depth Column checked" % name))
#     # elif abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values)))) < 2:
#     #     print("MINOR Error in scale of %s, off by %s units" % (name, diff))
#     else:
#         print(red_text("Status 12 - Possible error in scale of %s.\nValues are %s" % (name, np.diff(list_values))))
#     return np.diff(list_values)
#
#
# '''
# INITIALIZING MAIN MODULE FOR EXECUTION
#
# - SCRIPT OBTAINED FROM https://stackoverflow.com/questions/22898145/how-to-extract-text-and-text-coordinates-from-a-pdf-file
# - Open PDF and obtain file extents. Mainly "y_top" that will be used for further processing.
# - Size of MEDIABOX returned in points.
# '''
#
#
# def initial_processing():
#     global tot_len
#     print("LOADING %s. Please be patient..." % red_text(os.path.basename(pdf_name)))
#     # Create a PDF parser object associated with the file object.
#     parser = PDFParser(fp)
#
#     # Create a PDF document object that stores the document structure.
#     # Password, if any, for initialization as 2nd parameter
#     document = PDFDocument(parser)
#
#     # Check if the document allows text extraction. If not, abort.
#     if not document.is_extractable:
#         raise PDFTextExtractionNotAllowed
#
#     # Create a PDF resource manager object that stores shared resources.
#     rsrcmgr = PDFResourceManager()
#
#     # Create a PDF device object.
#     device = PDFDevice(rsrcmgr)
#
#     # BEGIN LAYOUT ANALYSIS
#     # Set parameters for analysis.
#     laparams = LAParams()
#
#     # Create a PDF page aggregator object.
#     device = PDFPageAggregator(rsrcmgr, laparams=laparams)
#
#     # Create a PDF interpreter object.
#     interpreter = PDFPageInterpreter(rsrcmgr, device)
#
#     # Total number of pages in PDF.
#     tot_pages = (resolve1(document.catalog['Pages'])['Count'])
#     page_count = 1
#
#     # loop over all pages in the document
#     for page in PDFPage.create_pages(document):
#
#         # read the media box that is the page size as list of 4 integers x0 y0 x1 y1
#         print("PAGE %s DIMENSIONS is %s points." % (page_count, page.mediabox))
#         _, _, _, tot_len = page.mediabox
#
#         # read the page into a layout object
#         # receive the LTPage object for this page
#         # from multiprocessing.dummy import Pool as ThreadPool
#         # pool = ThreadPool(4)
#         interpreter.process_page(page)
#         # pool.close()
#         # pool.join()
#
#         # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
#         layout = device.get_result()
#
#         # load module to parse every object encountered in the PDF
#         print("PDF PAGE %s / %s LOADED." % (bold_text(page_count), bold_text(tot_pages)))
#         parse_obj(layout._objs)
#
#         # Convert PDF to process lithology column and obtain Pt./Pixel Ratio
#         processing(defined_color_map)
#
#         # Crop PDF to precess the biogenic column
#         cropping_pdf()
#
#         # Increase page count
#         page_count += 1
#
#
# '''
# LOAD FOLDER
#
# - Load folder that contains all the templates to be matched.
# '''
#
#
# def load_templates(template_folder):
#     templates_folder = []
#     for root, path_dir, filenames in os.walk(template_folder):
#         for filename in filenames:
#             templates_folder.append(os.path.join(root, filename))
#     templates_folder = sorted(templates_folder)
#     return templates_folder
#
#
# '''
# CROP PDF
#
# - Load entire PDF
# - Crop off PDF and return new MediaBOX bound PDF.
# - Convert that MediaBOX to allow higher resolution PNG to be created .
# '''
#
#
# def cropping_pdf():
#     with open(pdf_name, "rb") as in_f:
#         log_input = PdfFileReader(in_f)
#         x1, y1, x2, y2 = log_input.getPage(0).mediaBox
#         numpages = log_input.getNumPages()
#         sed_struc_log_output = PdfFileWriter()
#
#         # Crop off the sed_biogenic column
#         for i in range(numpages):
#             sed_struc_log = log_input.getPage(i)
#             sed_struc_log.mediaBox.lowerLeft = (240, y2)
#             sed_struc_log.mediaBox.upperRight = (215, y1)
#             sed_struc_log_output.addPage(sed_struc_log)
#
#         # Write cropped area as a new PDF
#         with open((os.path.join(os.path.dirname(os.path.splitext(pdf_name)[0]), "sed_struc_log.pdf")), "wb") as out_f:
#             sed_struc_log_output.write(out_f)
#         out_f.close()
#
#         # Open PDF and convert to PNG (h_resol) for image processing.
#         out_f = (os.path.join(os.path.dirname(os.path.splitext(pdf_name)[0]), "sed_struc_log.pdf"))
#         convert(out_f, h_resol)
#
#         # Load image, template folder and execute matching module using biogenic parameters and threshold
#         cropped_pdf_image = (os.path.join(os.path.dirname(os.path.splitext(pdf_name)[0]), "sed_struc_log_python_convert.png"))
#         template_folder = os.path.join((os.path.dirname(os.path.splitext(pdf_name)[0])), "templates")
#         if not os.path.exists(template_folder):  # Check to see if the folder exists
#             os.makedirs(template_folder)  # if not then makes the folder
#             shutil.copyfile('/home/aly/Desktop/log2/a9j/templates/bio_04.png', template_folder)
#         # template_folder = os.path.join((os.path.dirname(os.path.splitext(pdf_name)[0])), "templates")
#         matching(cropped_pdf_image, template_folder, 0.70)  # match => pdf_image, folder holding template, matching threshold
#
#
# '''
# MATCH IMAGE & DISPLAY RESULT
#
# - Match the templates from the folder to their respective locations within the cropped image.
# - Templates are resized from 90 -110% of their size to look for more matches.
# - During matching the ratio of tracking is tracked.
# - Match proximity of based on half the smallest diagonal of the all template image..
# '''
#
#
# def matching(match_fil_name, folder, threshold):
#     matched, temp_locations = {}, []
#     templates_folder = load_templates(folder)  # Load Templates from Folder
#     print(green_text("\nProcessing %s - PNG Mode\nFound %s templates in folder" % (os.path.basename(folder).upper(), len(templates_folder))))
#     img_bgr = cv2.imread(os.path.abspath(match_fil_name))  # Read Image as RGB
#     img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)  # Convert Image to grayscale
#     cv2.imwrite(os.path.join(os.path.dirname(match_fil_name), 'gray_image.png'), img_gray)  # Write binary Image
#     _, temp_w, temp_h = img_bgr.shape[::-1]  # Tuple of number of rows, columns and channels
#     print("\nImage Loaded - Dimensions %s px X %s px @ %s dpi.\nPixel to Point ratio is: %.2f" % (temp_w, temp_h, h_resol, ratio_px_pt))
#
#     global unique_loc
#     remove, unique_loc = [], []  # reset every time loop is initialised?
#     list_r = []
#
#     # Lookup every image in the template folder.
#     for count, name in enumerate(templates_folder):
#         # remove, unique_loc, = [], []  #reset every time loop is initialised
#         color = list([random.choice(range(0, 256)), random.choice(range(0, 256)), random.choice(range(0, 256))])  # Random Color choice
#         template = cv2.imread(os.path.abspath(name), 0)  # Read Template Image as RGB
#         # template = imutils.resize(template, width=int(template.shape[1] * 2))  # In case scale is changed in future
#         w, h = template.shape[::-1]
#         r = ((h**2 + w**2) ** 0.5)
#         list_r.append(r / 2)
#         # resize the image according to the scale, and keep track of the ratio of the resizing
#         # resize from min to max scale at the spacing of 0.1
#         max_scale, min_scale = 1.3, 0.7
#         spacing = int((max_scale - min_scale) / 0.1)
#         for scale in np.linspace(min_scale, max_scale, spacing + 1)[::-1]:
#             # resize the image according to the scale, and keep track of the ratio of the resizing
#             resized = imutils.resize(template, width=int(template.shape[1] * scale))
#             # r = template.shape[1] / float(resized.shape[1]) #ratio
#             res = cv2.matchTemplate(img_gray, resized, cv2.TM_CCOEFF_NORMED)  # Match template to image using normalized correlation coefficient
#             loc = np.where(res >= threshold)  # Obtain locations, where threshold is met. Threshold defined as a function input
#             for pt in zip(*loc[::-1]):  # Goes through each match found
#                 temp_locations.append(pt)
#
#         # Sort matches based on Y location.
#         # temp_locations = sorted(temp_locations, key=itemgetter(1, 0))
#
#     # Look for the unique points.
#     # Minimum distance between matches set as half the smallest diagonal of the all template image.
#     unique = recursiveCoord(temp_locations, min(list_r))
#     unique = sorted(unique, key=itemgetter(1, 0))
#
#     # Draw a color coded box around each matched template.
#     print(len(temp_locations), len(unique))
#     for pt in temp_locations:
#         cv2.rectangle(img_bgr, pt, (pt[0] + w, pt[1] + h), color, 2)
#         unique_loc.append(pt[1])
#
#     print("Found %s matches." % bold_text(len(temp_locations)))
#     print("Found %s matches." % bold_text(len(unique)))
#
#     # Write image showing the location of the detected matches.
#     output_file_name = str(os.path.basename(folder) + '_detected.png')
#     cv2.imwrite(os.path.join(os.path.dirname(match_fil_name), output_file_name), img_bgr)
#     print(bold_text("Detected image saved.\n"))
#
#     write_to_csv(overall_dictionary, env_matches, color_dict, unique_loc)
#
#
# '''
# CHECKING PROXIMITY
#
# - Takes the first X/Y of the matched points and compares it to the remaining points.
# - Euclidean distance of Points within the threshold are deleted and the list updated.
# - Iterates till all the points are compared against each other.
# '''
#
#
# def recursiveCoord(_coordinateList, threshold):
#     if len(_coordinateList) > 1:
#         xy_0 = _coordinateList[0]
#         remaining_xy = list(set(_coordinateList) - set(xy_0))
#
#         new_xy_list = []
#
#         for coord in remaining_xy:
#             dist = distance.euclidean(xy_0, coord)
#
#             if dist >= threshold:
#                 new_xy_list.append(coord)
#
#         return [xy_0] + recursiveCoord(new_xy_list, threshold)
#     else:
#         return []
#
#
# '''
# FIND / RENAME MODULE
#
# - Inverted images are converted using pdftoppm utility to convert PDF to PIL Image object.
# - Utility does not allow for file name handling, name found by extension and then name changed.
# '''
#
#
# def find(pattern, path):
#     result = []
#     for root, dirs, files in os.walk(path):
#         for name in files:
#             if fnmatch.fnmatch(name, pattern):
#                 result.append(os.path.join(root, name))
#     return result
#
# def rename(new_f_name):
#     time.sleep(5)
#     names = find('*-1.png', os.path.dirname(new_f_name))
#     fil_name = os.path.splitext(new_f_name)[0] + '_python_convert.png'
#     for i in names:
#         os.rename(i, os.path.join(os.path.dirname(new_f_name), fil_name))
#         # print(os.rename(i, os.path.join(os.path.dirname(new_f_name), fil_name)))
#     return names
#
# '''
# CONVERT PDF TO PNG
#
# - Loads PDF log and returns PNG at specified pixel
# '''
#
#
# def convert(f_name, conv_resol):
#     global fil_name, look_for
#     from wand.image import Image
#     from wand.color import Color
#     import wand.exceptions
#     from pdf2image import convert_from_path, convert_from_bytes
#
#     try:
#         with Image(filename=f_name, resolution=conv_resol) as img:
#             with Image(width=img.width, height=img.height, background=Color("white")) as bg:
#                 bg.composite(img, 0, 0)
#                 # bg.alpha_channel = False
#                 bg.save(filename=os.path.splitext(f_name)[0] + '_python_convert.png')
#         fil_name = os.path.splitext(f_name)[0] + '_python_convert.png'
#     except wand.exceptions.CorruptImageError or TypeError:
#         print(red_text("INVERTED IMAGE - PDF File maybe corrupted"))
#         convert_from_path(f_name, dpi=conv_resol, output_folder=os.path.join(os.path.dirname(f_name)), first_page=1,
#                           last_page=None, fmt='png')
#         rename(f_name)
#         fil_name = os.path.splitext(f_name)[0] + '_python_convert.png'
#
#     if platform.system() == "Linux":
#         im = PIL.Image.open(fil_name)
#         rgb_im_neg = im.convert('RGB')
#         if get_colour_name(rgb_im_neg.getpixel((5,5)))[1] == 'black':
#             print(red_text('Negative Image\nConverting Image'))
#             convert_from_path(f_name, dpi=conv_resol, output_folder=os.path.join(os.path.dirname(f_name)), first_page=1,
#                               last_page=None, fmt='png')
#             rename(f_name)
#         im.close()
#         fil_name = os.path.splitext(f_name)[0] + '_python_convert.png'
#
#     # print(fil_name)
#     look_for = 'black'
#
#
# '''
# GET PNG / PDF RATIO
#
# - Obtain height of PNG
# - Obtain total length of PDF
# - Return Ratio
# '''
#
#
# def ratio():
#     global ratio_px_pt
#     # print(height, tot_len)
#     ratio_px_pt = height / tot_len
#     return ratio_px_pt
#
#
# '''
# POLYFIT OF LINE
#
# - Fits a linear correlation in mx + c format
# - returns GLOBAL m and c
# '''
#
#
# def coeff(mx, my):
#     global m, c
#     z = np.polyfit(mx, my, 1)
#     m, c = z[0], z[1]
#     return m, c
#
#
# '''
# CHECK BEDDING
#
# - Loads the location of the black lines
# - Checks on the right and left to ensure that line constitutes of mainly black
# - In the event that only white/black are encountered and white is more, another check is carried out to ensure that the ratio of black / white is more than 80%
# - The above is the attempt to overcome the problem with the dashed lines
# '''
#
#
# def bed(approx_x, neg, pos, location_to_check):
#     # print("\nPossible Depth (m) at X = %s: Top 2 Most Common colors on that line (RGB Color / Count)" % approx_x)
#     global contact_type
#     contact_type = []
#     for i in location_to_check:
#         bedding_surface = []
#         for k in range(approx_x - neg, approx_x + pos):
#             bedding_surface.append(rgb_im.getpixel((k, i)))
#         # print("%0.3f : %s" % ((m * (height - i) / ratio_px_pt) + c, Counter(bedding_surface).most_common(2)))
#         if get_colour_name(Counter(bedding_surface).most_common(1)[0][0])[1] == look_for:
#             contact_type.append((m * (height - i) / ratio_px_pt) + c)
#         elif get_colour_name(Counter(bedding_surface).most_common(2)[0][0])[1] == 'white' and get_colour_name(Counter(bedding_surface).most_common(2)[1][0])[1] == look_for and Counter(bedding_surface).most_common(2)[1][1] / Counter(bedding_surface).most_common(2)[0][1] > 0.50:
#             # print("WHITE / BLACK")
#             contact_type.append((m * (height - i) / ratio_px_pt) + c)
#
#     return contact_type
#
#
# '''
# RUNNING GROUPS
#
# - Loads a list and groups consecutive numbers with a tolerance
# - In this case the tolerance is 1. i.e., 5 and 7 would be in one group.
# '''
#
#
# def group_runs(li, tolerance=1):
#     out = []
#     last = li[0]
#     for x in li:
#         if x-last > tolerance:
#             yield out
#             out = []
#         out.append(x)
#         last = x
#     yield out
#
#
# '''
# IMAGE COLOR INITIALISATION
#
# - Loads Image
# '''
#
#
# def load_image(file_name):
#     global rgb_im, width, height
#     # Image.MAX_IMAGE_PIXELS = None # Override to PIXEL processing limitation. This will tremendously increase processing time.
#     # Load Image
#     im = Image.open(file_name)
#     # Convert to RGB
#     rgb_im = im.convert('RGB')
#     # Obtain image dimension for digitization
#     width, height = im.size
#     return rgb_im, width, height
#
#
# '''
# IMAGE COLOR INITIALISATION
#
# - Obtains all colors (1 pixel wide) at X location
# - Reduces colors to the user defined unique colors + White (blank space)
# '''
#
#
# def processing(the_defined_color_map):
#     convert(pdf_name, resol)  # Convert pdf at the specified resolution
#     load_image(fil_name)  # Load image and obtain necessary information
#     ratio()  # Calculate ratio
#     color_map = []
#     approx_x = 620  # Predefined location
#     processing_HZ_lines()
#
#     print(green_text("\nProcessing color column - PNG Mode"))
#     print("\nImage Loaded - Dimensions %s px X %s px @ %s dpi.\nPixel to Point ratio is: %.2f" % (width, height, resol, ratio_px_pt))
#
#     # Obtain All Colors (1 Color/pixel) in the Lithological Identification
#     for j in range(0, height, 1):
#         # print (j, rgb_im.getpixel((approx_x, j)), get_colour_name(rgb_im.getpixel((approx_x, j)))[1])
#         color_map.append(rgb_im.getpixel((approx_x, j)))
#
#     print("No. of existing colors in Pixel ID %s column is: %s" % (bold_text(approx_x), bold_text(len(set(color_map)))))
#
#     unique_color_map = the_defined_color_map  # Colors used in cleanup
#     print("Looking up a total of %s defined colors." % bold_text(len(set(unique_color_map))))
#
#     print(bold_text("\nUser defined Colors:\n"))
#     for i in unique_color_map:
#         print("RGB: %s \t- Closest RGB colour name: %s" % (i, bold_text(get_colour_name(i)[1])))
#
#     # MOVE TO NEXT MODULE - IMAGE CLEANUP
#     # print(color_map)
#     log_cleanup(color_map, unique_color_map)
#
#
# '''
# PROCESS THE HORIZONTAL LINES
#
# - Checks for the horizontal lines in the PDF log (ALL_PNG)
# - Checks for the horizontal lines in the PDF log (ENV_PNG)
# - Will TERMINATE if the line COUNT is different. Meaning, the code/log has to be examined thoroughly.
# - If the lines mismatch in depth, a warning will be displayed.
# '''
#
#
# def processing_HZ_lines():
#     print(green_text("\nProcessing Hz lines - PNG Mode"))
#     HZ_lines = {}
#     print("Image Loaded - Dimensions %s px X %s px @ %s dpi.\nPixel to Point ratio is: %.3f" % (width, height, 300, ratio_px_pt))
#     approx_x = {1525: ['ALL_PNG', 740, 5], 2110: ['ENV_PNG', 515, 355]}  # FATAL ERROR IS TRACED To HERE!
#
#     # Save location if black is identified along the height at the approx X location
#     for k, v in approx_x.items():
#         location_to_check = []
#         black_lines = []
#         for j in range(0, height):
#             # print(j, rgb_im.getpixel((k, j)), get_colour_name(rgb_im.getpixel((k, j)))[1])
#             # print(look_for)
#             if get_colour_name(rgb_im.getpixel((k, j)))[1] == look_for:
#                 # print("BLACK LINES", j)
#                 black_lines.append(int(j))
#
#         # Check if the locations are after one another and group them
#         possible_black_lines = list(group_runs(black_lines))
#
#         # After grouping, check the center point of the line.
#         for i in (possible_black_lines):
#             # print(i)  # DISPLAY Location of possible black lines.
#             location_to_check.append((sum(i) / len(i)))
#
#         # Check along the X of those locations
#         bed(k, v[1], v[2], location_to_check)
#         # The return variable is based on the approx_x name
#         HZ_lines[v[0]] = contact_type
#
#     ALL_PNG = HZ_lines['ALL_PNG']
#     ENV_PNG = HZ_lines['ENV_PNG']
#
#     # Checks to ensure the number of lines in ALL_PNG and ENV_PNG are the same.
#     # If NOT TERMINATES
#     # If the same count but at different depth, will return a warning.
#     if len(ALL_PNG) == len(ENV_PNG):
#         for x in range(len(ALL_PNG)):
#             if -10 < ALL_PNG[x] - ENV_PNG[x] < 10:
#                 continue
#             else:
#                 print(ALL_PNG[x], ENV_PNG[x], "Non match")
#     elif abs(len(ENV_PNG) - len(ALL_PNG)) == 1:
#         print(red_text("MINOR MISMATCH - PROCEEDING\nPLEASE CHECK THOROUGHLY"))
#         if not (list(set(ENV_PNG) - set(ALL_PNG))):
#             print(red_text("Check Depths: \t%s" % list(set(ALL_PNG) - set(ENV_PNG))))
#         else:
#             print(red_text("Check Depths in Environment Column: \t%s" % list(set(ENV_PNG) - set(ALL_PNG))))
#         # print((ENV_PNG))  # Print depth of black lines in Environmental deposition
#         # print((ALL_PNG))  # Print depth for the remainder of the log.
#         ENV_PNG = ALL_PNG
#     else:
#         print(red_text("LINE IN ALL PNG AND ENV PNG DO NOT MATCH\nPROCEED WITH CAUTION\nThe following depths indicate discrepancy"))
#         if not list(set(ENV_PNG) - set(ALL_PNG)):
#             print("Check Horizontal Depths at: \t%s" % list(set(ENV_PNG) - set(ALL_PNG)))
#         else:
#             print("Check Horizontal Depths at: \t%s" % list(set(ALL_PNG) - set(ENV_PNG)))
#         ENV_PNG = ALL_PNG
#
#
#         # exit("FATAL ERROR!")
#
#     # DISPLAY Location of Hz black lines.
#     # print("\nDepth of identified Hz lines (m)")
#     # for i in ALL_PNG:
#     #     print("%0.3f" % i)
#
#     # Transform the identified HZ lines into groups.
#     # TOP : [TOP, BOTTOM]
#     final_dict = {}
#
#     zipped = list(zip(ALL_PNG, ALL_PNG[1:]))
#
#     for a, x in enumerate(ALL_PNG):
#         if a < (len(ALL_PNG) - 1):
#             final_dict[x] = list(zipped[a])
#
#     global overall_dictionary
#
#     overall_dictionary = OrderedDict(sorted(final_dict.items()))
#     print(green_text("\nProcessed Hz lines - PNG Mode\n"))
#
#     # DISPLAY identified layer depths.
#     print(bold_text("Identified Layers\nDepth from (m) : Depth to (m)"))
#     for k, v in overall_dictionary.items():
#         print("%0.3f : %0.3f" % (v[0], v[1]))
#
#
# '''
# LOG CLEANUP
#
# - Remove pixelated color making the log equivalent to the unique set defined
# '''
#
#
# def log_cleanup(cleanup_color_map, unique_color_map):
#
#     for i in range(1, len(cleanup_color_map)):
#         if cleanup_color_map[i] not in unique_color_map:
#             col_nam = get_colour_name(cleanup_color_map[i])[1]
#             cleanup_color_map[i] = (webcolors.name_to_rgb(col_nam)[0], webcolors.name_to_rgb(col_nam)[1], webcolors.name_to_rgb(col_nam)[2])
#         # if get_colour_name(cleanup_color_map[i])[1] == 'darkslategrey':
#         #     cleanup_color_map[i] = (0, 0, 0)
#
#     for i in range(1, len(cleanup_color_map)):
#         if cleanup_color_map[i] not in unique_color_map:
#             cleanup_color_map[i] = cleanup_color_map[i - 1]
#
#     # DISPLAY the cleaned up color map
#     # for x,i in enumerate(cleanup_color_map):
#     #     print(x, get_colour_name(i)[1])
#
#     # ## MOVE TO NEXT MODULE - REMOVE LINES
#     remove_black_lines(cleanup_color_map)
#
#
# '''
# REMOVE LINES
#
# - Remove black lines (dividers)
# - Splits the pixel thickness of the line and divides it into the upper and lower lithology
# '''
#
#
# def remove_black_lines(color_map):
#     location = []
#     black_lines, location_to_check = [], []
#
#     for j in range(0, height):
#         if get_colour_name(color_map[j])[1] == look_for:
#             black_lines.append(int(j))
#
#     possible_black_lines = list(group_runs(black_lines))
#
#     # After grouping, split line and divide into top and bottom colors.
#     for y, i in enumerate(possible_black_lines):
#         # print("Line # %s" % y)
#         for x in i:
#             if x < (sum(i) / len(i)):
#                 color_map[x] = color_map[min(i) - 1]
#             else:
#                 color_map[x] = color_map[max(i) + 1]
#
#     for h, k in enumerate(location):
#         color_map[k] = color_map[min(location) - 1]
#
#     global color_dict
#     color_dict = {}
#     for i, j in enumerate(color_map):
#         # print("%.3f %s %s" %(m * ((len(color_map) - i) / ratio_px_pt) + c, j, get_colour_name(j)[1]))
#         color_dict[m * ((len(color_map) - i) / ratio_px_pt) + c] = get_colour_name(j)[1]
#
#     print(green_text("\nProcessed color column"))
#     # DISPLAY DEPTH : COLORS
#     # print("Depth (m) : Color")
#     # for k, v in color_dict.items():
#     #     print("%0.3d : %s" % (k, v))
#
# # '''
# # FACIES CODE
# #
# # - Criteria based on Dr. Moslow Email
# # - Identifies the logic of the facies code, in accordance to the legend
# # '''
# #
# # def facies_code(env_name, litho_color):
# #     if env_name == 'LS':
# #         f_code = str(1)
# #     elif env_name == 'OT':
# #         f_code = str(2)
# #     elif env_name == 'OTP':
# #         f_code = str(3) + 'A'
# #     elif env_name in ('OTP/T', 'OTP / T', 'T/OTP', 'T / OTP'):
# #         f_code = str(3) + 'B'
# #     elif env_name == 'OTD':
# #         f_code = str(4) + 'A'
# #     elif env_name in ('OTD/T', 'OTD / T', 'T/OTD', 'T / OTD'):
# #         f_code = str(4) + 'B'
# #     elif env_name == 'O' and litho_color in ('Bituminous F-C Siltstone', 'Bituminous F-M Siltstone'):
# #         f_code = str(5) + 'A'
# #     elif env_name == 'O' and litho_color in ('Phosphatic - Bituminous Sandy Siltstone to Breccia'):
# #         f_code = str(5) + 'B'
# #     elif env_name in ('H', 'Hemipelagite'):
# #         f_code = str(6)
# #     elif env_name in ('Tempestites', 'Tempestite', 'T') and litho_color in ('Sandy F-C Siltstone to Silty VF Sandstone'):
# #         f_code = str(7) + 'A'
# #     elif env_name in ('Tempestites', 'Tempestite', 'T') and litho_color in ('Laminated Bedded Resedimented Bioclasts'):
# #         f_code = str(7) + 'B'
# #     elif env_name == 'Seismite':
# #         f_code = str(8)
# #     elif env_name == 'T. Lag' and litho_color in ("Phosphatic - Bituminous Sandy Siltstone to Breccia"):
# #         f_code = str(9) + 'A'
# #     elif env_name == 'T. Lag' and litho_color in ('Laminated Bedded Resedimented Bioclasts'):
# #         f_code = str(9) + 'B'
# #     elif env_name == 'Turb':
# #         f_code = str(10)
# #     else:
# #         f_code = "UNKNOWN"
# #     return f_code
#
#
# '''
# OUTPUT TO CSV FORMAT
#
# - Outputs to Terminal, for easy visualization
# - Outputs to CSV as LAS, with the range period specified
# - Outputs as layer sequence based on the sequencing obtained from the HZ lines
# '''
#
#
# def write_to_csv(h_lines, env, color, bl_unique_loc):
#     LAS_Interval = 0.1 # This is the interval that defined how often to output a depth in the LAS File type output.
#     print(green_text("\nProcessing CSV Information"))
#     # Sort all dictionaries
#     h_lines = OrderedDict(sorted(h_lines.items(), key=lambda t: t[0]))
#     env = OrderedDict(sorted(env.items(), key=lambda t: t[0]))
#     color = OrderedDict(sorted(color.items(), key=lambda t: t[0]))
#
#     # List of dictionaries that will be merged into the main dictionary
#     list_of_dict = [env, ]
#     list_of_dict_names = ["ENVIRONMENT", ]
#
#     # Checks all the keys in the dictionary that they lie in a depth interval.
#     int_counter = 2
#     for nam, dict_name in enumerate(list_of_dict):
#         print(bold_text("READING %s" % (list_of_dict_names[nam])))
#         for k, v in h_lines.items():
#             for k1, v1 in list(dict_name.items()):
#                 if v[0] < k1 < v[1]:
#                     h_lines[k].append(v1)
#                     del dict_name[k1]  # Removes that matched key:value and reiterates
#
#         # Highlights any unmatched items
#         if not dict_name:
#             print(green_text("EVERYTHING in %s HAS BEEN MATCHED" % list_of_dict_names[nam]))
#         else:
#             print(red_text("The following has not been matched"))
#             print(dict_name)
#             # for k2, v2 in dict_name.items():
#             #     print(red_text("$s - %s" % (k2, v2)))
#
#         # Parsing the data in the environments.
#         # Code is limited by the inconsistency of the 'Enter' values and manual adjustments of the text box.
#         all_values = []
#         for k in h_lines.keys():
#             if len(h_lines[k][int_counter:]) == 1:
#                 # print(green_text("MATCH %.3f - %s" % (k, h_lines[k])))
#                 continue
#             elif len(h_lines[k][int_counter:]) > 1:
#                 print(red_text("PLEASE CHECK %.3f - %s" % (k, h_lines[k][2:])))
#                 if h_lines[k][int_counter:][1] == h_lines[k][int_counter:][0]:
#                     print(green_text("Considered as similar environment - %s" % h_lines[k][int_counter:][1]))  # If same ENV encountered within the same depth interval
#                     all_values.append(h_lines[k][int_counter:][1])
#                     a = ([''.join(h_lines[k][int_counter:][1])])  # Consider them as one.
#                     h_lines[k][int_counter:] = a
#                 else:
#                     print(h_lines[k][int_counter:])
#                     all_values.append([' ? '.join(h_lines[k][int_counter:])])
#                     a = ([' ? '.join(h_lines[k][int_counter:])])  # If more than one value of ENV encountered within the same depth interval without a '/'
#                     h_lines[k][int_counter:] = a
#             else:
#                 all_values.append(h_lines[k][int_counter:])
#
#         print(red_text("EMPTY ENTRIES FOUND IN %s ARE BEING POPULATED AS \'UNKNOWN\'" % list_of_dict_names[nam]))
#         for k in h_lines.keys():
#             if len(h_lines[k]) < int_counter + 1:
#                 h_lines[k].append("UNKNOWN")
#
#         int_counter += 1
#
#     # Calculating the percentage lithology within each depth interval.
#     for k, v in h_lines.items():
#         cat_val = []
#         for k1, v1 in list(color.items()):
#             if v[0] < k1 < v[1]:
#                 cat_val.append(v1)
#         x = Counter(cat_val)
#         cat_dict = (dict([(i, round(x[i] / len(cat_val) * 100.0)) for i in x]))  # Change counter mode to %
#         cat_dict = dict((litho_legend[key], value) for (key, value) in cat_dict.items())  # Change RGB to Lithology name
#         val = (sorted(cat_dict.items(), key=lambda y: y[1], reverse=True))  # Value to return to Dictionary
#         h_lines[k].append(val)
#
#     # Cleaning blank space from being output
#     # If white presents 99/100 % of the color along that line
#     for k, v in list(h_lines.items()):
#         if list(v[3][0])[0] == 'Blank Space' and list(v[3][0])[1] in [99, 100]:
#             del h_lines[k]
#
#     for k, v in h_lines.items():
#         cat_temp_val = []
#         for k1 in unique_loc:
#             k1 = (m * (height - (k1 / 2)) / ratio_px_pt) + c
#             if v[0] < k1 < v[1]:
#                 cat_temp_val.append(k1)
#         x = len(cat_temp_val)
#         h_lines[k].append(x)
#
#     # Output to LAS File
#     # print to Terminal window
#     import bisect
#     # print("Reading")
#     layered_output = os.path.join(os.path.dirname(pdf_name), os.path.splitext(os.path.basename(pdf_name))[0] + '_updated_Layered_output.csv')
#     depth_min, depth_max, dep_env, percent = [], [], [], []
#     with open(layered_output, 'r') as readcsv:
#         reader = csv.DictReader(readcsv)
#         for row in reader:
#             depth_min.append(float(row["Depth From (m)"]))
#             depth_max.append(float(row["Depth To (m)"]))
#             dep_env.append((float(row["Depth To (m)"]), row["Depositional Environment"], row["Biogenic"]))
#
#         # print(min(depth_min))
#         # print(max(depth_max))
#
#         print(green_text("\nFINAL OUTPUT\nLAS FORMAT\n"))
#         LAS_output = os.path.join(os.path.dirname(pdf_name), os.path.splitext(os.path.basename(pdf_name))[0] + '_updated_LAS_output.csv')
#         with open(LAS_output, 'w') as writecsv:
#             writer = csv.writer(writecsv, lineterminator='\n')
#             writer.writerow(["Depth (m)", "Facies Code", "Depositional Environment", "Lithology", "No. Biogenic", "Percentages"])
#             for k, v in h_lines.items():
#                 # a = float(v[1])
#                 # # print(a)
#                 # a = "{0:.1f}".format(a)
#                 # percent.append((a, v[3]))
#                 # print(percent)
#                 percent.append((v[1], v[3]))
#                 # print(k,v)
#             for i in np.arange(min(depth_min), max(depth_max), LAS_Interval):
#                 # i = "{0:.1f}".format(i)
#                 # i = j - LAS_Interval
#                 color_at_def_depth = color.get(i) or color[min(color.keys(), key=lambda z: abs(z - i))]
#                 pos = bisect.bisect_right(dep_env, (i,))
#                 pos_left = bisect.bisect_right(percent, (i,))
#                 # print('%s -> %s' % (i, dep_env[pos]))
#                 # print('%s -> %s' % (i, percent[pos_left]))
#                 if color_at_def_depth in litho_legend:
#                     litho = litho_legend[color_at_def_depth]
#                 else:
#                     litho = color_at_def_depth
#                 f_code = facies_code(dep_env[pos][1], litho)
#                 print("DEP ENV", dep_env)
#                 # print('%.1f \t%s \t%s \t%s \t%s' % (round(i, 1), v[2], litho, v[4], v[3]))  # Print to terminal window
#                 writer.writerow(["{0:.1f}".format(i), f_code, dep_env[pos][1], litho, dep_env[pos][2]] + percent[pos_left][1])
#         writecsv.close()
#         print(green_text("LAS output file written"))
#
# def findSubdirectories(dir_path):
#     sub_dirs = []
#     for root, dirs, files in os.walk(dir_path):
#         # for dir_name in dirs:
#         for filename in files:
#             if filename.endswith(('.pdf')):
#
#                 # print (os.path.join(root,name))
#                 sub_dirs.append(os.path.join(root, filename))
#                 # print (os.path.join(root,name))
#                 # sub_dirs.append(os.path.join(root, dir_name, filename))
#     sub_dirs = sorted(list(set(sub_dirs))) # Sort directories alphabetically in ascending order
#     print("Found \033[1m%s\033[0m sub-directories" % len(sub_dirs))
#     return sub_dirs
#
# '''
# MAIN MODULE
#
# - Returns total time and Error on user termination.
# '''
#
# def main(argv):
#     # Parse arguments from user
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-f', '--file', type=str, required=False, default='/home/aly/Desktop/Progress_Energy/post_processed/c-7-J_94-B-8_(1)_(revised)/c-7-J_94-B-8_(1)_(revised).pdf',
#                         help="Path to PDF file for processing")
#     parser.add_argument('-b', '--batch', action="store_true",
#                         help="Batch process of output files in the subdirectories of the given directory")
#     args = parser.parse_args()
#
#     # If '.' is specified, the current directory is used as the directory path
#     if args.file == '.':
#         args.file = os.getcwd()
#
#     # Placeholder for the list of directory(ies). Change relative path to absolute path.
#     directories = [os.path.abspath(args.file)]
#
#     # If batch processing, we'll need to do the analysis on all subdirectories of the given directory
#     if args.batch:
#         print('\nBatch processing...\n')
#
#         directories = findSubdirectories(os.path.abspath(args.file))
#
#     # Loop over directory(ies)
#     if directories is not None and directories:
#         for sub_dir in directories:
#             print(sub_dir)
#             open_file(sub_dir)
#
# if __name__ == "__main__":
#     try:
#         import multiprocessing
#         q = sys.argv[1:]
#         p = multiprocessing.Process(target=main, args=(q,))
#         p.start()
#         p.join()
#         print("\nTotal Execution time: \033[1m%s\033[0m\n" % calc_timer_values(time.time() - abs_start))
#     except KeyboardInterrupt:
#         exit("TERMINATED BY USER")
