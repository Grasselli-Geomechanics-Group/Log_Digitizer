# /////////////////////////////////////////////////////////////// #
# !python2.7
# -*- coding: utf-8 -*-
# Python Script initially created on 12/05/2018
# Compiled by Aly @ Grasselli's Geomechanics Group, UofT, 2018
# Created using PyCharm // Tested on Spyder
# Current Version 03 - Dated July 20, 2018
# /////////////////////////////////////////////////////////////// #

## This code was compiled based on the layout of d_66_I_94_B_16_Continuous_Core Log

# V01
#   - Initial release

# V02
#   - Code optimization {Split into different modules}
#   - Modules run for different pixel columns as defined.
#   - Identifies depositional bedding type.

# V03
#   - Adjust scale based on dpi
#   - Code optimization {Algorithm changed}
#   - Changed colors in terminal outputs
#   - PDF split into MediaBOX to have a higher resolution image during template mataching.
#   - Template matching functional

from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader
from operator import itemgetter
from collections import Counter
import time, os, webcolors, csv, cv2, random
import numpy as np

abs_start = time.time()

'''
COMPILING VARIABLES AND USER INPUTS
    # Required User Inputs
        # - No. of unique colors
        # - Excluded colors from mapping
        # - Two points on log with their depth and pixel location
'''
## Variables
litho_defined_number_of_unique_colors = 6 # No. of unique color sets in lithology column (legend)
surface_defined_number_of_unique_colors = 3 # No. of unique color sets in surfaces (legend)
top_of_log = 793  # top of lithology bar on a 300dpi @ Pixel 793
excluded_colors = [(255, 255, 255), (36, 31, 33), (94, 91, 92), (138, 136, 137), (197, 195, 196), (187, 233, 250), (26, 69, 87)]  # exclusion colors from mapping [(White), (Black), (Dim Grey), (Grey), (Silver), (paleturquoise), (darkslategray)]
pdf_name = '/home/aly/Desktop/Progress_Logs/d_66_I_94_B_16_Continuous_Core.pdf'
# fil_name = '/hdd/home/aly/Desktop/Dropbox/Python_Codes/Progress_BHLOG/d_66_I_94_B_16_Continuous_Core.pdf'
# fil_name = 'C:/Users/alica/Dropbox/Python_Codes/Progress_BHLOG/d_66_I_94_B_16_Continuous_Core-1.png'


## DICTIONARY
litho_legend = {"skyblue" : "Laminated Bedded Resedimented Bioclasts", "sandybrown" : "Bituminous F-C Siltstone", "tan" : "Bituminous F-M Siltstone", "khaki" : "Sandy F-C Siltstone to Silty VF Sandstone", "darkseagreen" : "Phosphatic - Bituminous Sandy Siltstone to Breccia", "plum" : "Calcareous - Calcispheric Dolosiltstone"}
surface_legend = {"deepskyblue" : "Marine Flooding Surface", "seagreen" : "Maximum Flooding Surface", "seagreen" : "Transgressive Surface of Erosion", "crimson" : "Sequence Boundary/Flooding Surface"}

## DIGITIZATION
depth = [1935, 1940]
pixel_id = [1267.5, 1741.5]
ratio = (pixel_id[1] - pixel_id[0]) / (depth[1] - depth[0])

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
CONVERT PDF TO PNG
    # - Loads PDF log and returns PNG at specified pixel
'''


def convert(pdf_name, resol):
    from wand.image import Image
    from wand.color import Color
    global fil_name
    with Image(filename=pdf_name, resolution=resol) as img:
        with Image(width=img.width, height=img.height, background=Color("white")) as bg:
            bg.composite(img, 0, 0)
            bg.save(filename=os.path.splitext(pdf_name)[0] + '_python_convert.png')
    fil_name = os.path.splitext(pdf_name)[0] + '_python_convert.png'

'''
INITIALISATION
    # - Loads Image
    # - Obtains all colors (1 pixel wide) at X location
    # - Reduces colors to an amount equal to the user defined unique colors
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
    # print("" % (width, height))
    return rgb_im, width, height


# Identifies locations that are to be processed for
# - Stratigraphical sequence (X - Pixel 775 on 300dpi) & Deposition Type
# - Surface Type sequence (X - Pixel 1005 on 300dpi)

def initial_processing():
    global csv_output, legend, x_approx, start
    start = time.time()
    # Image.MAX_IMAGE_PIXELS = None # Override to PIXEL processing limitation. This will tremendously increase processing time.
    resol = 300
    convert(pdf_name, resol)
    load_image(fil_name)
    print ("Image Loaded - Dimensions %s px X %s px.\nCompleted in : \033[1m%s\033[0m\n" % (width, height, calc_timer_values(time.time() - start)))
    # Approximate Locations on Image for Lithological Identification
    start = time.time()
    legend = litho_legend
    csv_output = 'stratigraphical_sequence.csv'
    x_approx = int((775./2550) * (resol / 300) * width)  # on a 300dpi @ Pixel 775
    y_start_approx_litho = int((float(top_of_log)/21300) * (resol / 300) * height)
    y_end_approx_litho = int((21178./21300) * (resol / 300) * height)  # on a 300dpi @ Pixel 21178
    # Load next module using Lithological Identification parameters
    processing(x_approx, y_start_approx_litho, y_end_approx_litho, litho_defined_number_of_unique_colors)

    # Approximate Locations on Image for Surface Type Identification
    start = time.time()
    legend = surface_legend
    csv_output = 'surface_sequence.csv'
    x_approx = int((1005./2550) * (resol / 300) * width)  # on a 300dpi @ Pixel 1005
    y_start_approx_surface = int((float(top_of_log)/21300) * (resol / 300) * height)
    y_end_approx_surface = int((21178./21300) * (resol / 300) * height)  # on a 300dpi @ Pixel 21178
    # Load next module using Surface Type Identification parameters
    processing(x_approx, y_start_approx_surface, y_end_approx_surface, surface_defined_number_of_unique_colors)

    ## Start matching process
    split_pdf(pdf_name)
    # matching()


# - Obtains all colors (1 pixel wide) at X location
# - Reduces colors to an amount equal to the user defined unique colors

def processing(approx_x, ystart, yend, defined_number_of_unique_colors):
    # reset variables
    color_map = []
    defined_color_map = []
    # Obtain All Colors (1 Color/pixel) in the Lithological Identification
    for j in range(ystart, yend):
        # print (j, rgb_im.getpixel((approx_x, j)))
        color_map.append(rgb_im.getpixel((approx_x, j)))

    print("\033[92m\033[1mProcessing %s.\033[0m\nNo. of existing colors in Pixel ID %s column is: %s" % (csv_output, approx_x, len(set(color_map))))
    color_map_mode = Counter(color_map)  # counts the frequency of RGB Colors
    color_map_mode = (sorted(color_map_mode.items(), key=lambda i: i[1], reverse=True))  # Sorts ascending based on frequency

    # Reduces the colors the (X) amount of the max occurring colors
    # X is user defined
    mode_counter = 0
    for i, j in enumerate(color_map_mode):
        if mode_counter < defined_number_of_unique_colors:
            for m, color in enumerate(j):
                if m == 0 and color not in excluded_colors:
                    defined_color_map.append(color)
                    mode_counter += 1

    unique_color_map = defined_color_map + excluded_colors # Colors used in cleanup
    print("\nLooking up defined and excluded colors. A total of : %s" % len(set(unique_color_map)))

    print("\n\033[1mUser defined No. of Colors\033[0m\n")
    for i in unique_color_map:
        # actual_name, closest_name = get_colour_name(i)
        print("RGB: %s \t- Closest RGB colour name: \033[1m%s\033[0m" % (i, get_colour_name(i)[1]))

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

    ## MOVE TO NEXT MODULE - REMOVE LINES
    remove_black_lines(color_map)

'''
REMOVE LINES
    # - Remove black lines (dividers)
    # - Splits the pixel thickness of the line and divides it into the upper and lower lithology
'''


def remove_black_lines(color_map):
    location = []
    for i in range(0, len(color_map) - 1):
        if color_map[i] == (36, 31, 33):
            if color_map[i] == color_map[i + 1]:
                location.append(i)
            else:
                location.append(i)
                for j, m in enumerate(location):
                    if m == 0:
                        color_map[m] = color_map[max(location) + 1]
                    elif j < (len(location) / 2):
                        color_map[m] = color_map[min(location) - 1]
                    else:
                        color_map[m] = color_map[max(location) + 1]
                location = []

    for h, m in enumerate(location):
        color_map[m] = color_map[min(location) - 1]

    color_map.pop()

    ## MOVE TO NEXT MODULE - DIGITIZE LOG
    digitized_log(color_map)

'''
DEFINE CONTACT INTERFACE
    # - Reads 100 pixels in the contact row and returns the depositional beds
    # - If all one color (smooth) else (rough)
'''


def bed(approx_x, approx_y):
    bedding_surface = []
    global contact_type
    for k in range(approx_x - 100, approx_x):
        bedding_surface.append(rgb_im.getpixel((k, approx_y)))
    if len(set(bedding_surface)) == 1:
        contact_type = "smooth"
    else:
        contact_type = 'rough'
    return contact_type

'''
DIGITIZE LOG
    # - Returns depth based on pixel location as defined by user
    # - Returns stratigraphical sequence (based on color)
    # - Returns depositional beds (based on color scheme along the contact surface)
'''


def digitized_log(color_map):
    ch_top = []
    output_file = os.path.join(os.path.dirname(fil_name), csv_output)
    with open(output_file, 'w') as writecsv:
        writer = csv.writer(writecsv)
        if legend == litho_legend:
            writer.writerow(["From (m)", "To (m)", "Color Code", "Lithofacies", "Contact to next Surface"])
        elif legend == surface_legend:
            writer.writerow(["From (m)", "To (m)", "Color Code", "Interface"])
        for i, j in enumerate(color_map):
            # if i in range(15000, 16000):
            if i < (len(color_map) - 1):
                ch_top.append(round((depth[0] + ((i + top_of_log - pixel_id[0]) / ratio)), 3))
                if color_map[i] != color_map[i + 1]:
                    ch = (round((depth[0] + ((i + top_of_log - pixel_id[0]) / ratio)), 3))
                    # LOAD MODULE TO CHECK CONTACT
                    if legend == litho_legend:
                        bed(x_approx, i + top_of_log)
                        writer.writerow(["{0:.3f}".format(min(ch_top)), "{0:.3f}".format(ch), get_colour_name(j)[1], legend.get(get_colour_name(j)[1]), contact_type])
                    elif legend == surface_legend:
                        writer.writerow(["{0:.3f}".format(min(ch_top)), "{0:.3f}".format(ch), get_colour_name(j)[1], legend.get(get_colour_name(j)[1])])
                    ch_top = []
    print ("\nCompleted in : \033[1m%s\033[0m\n" % calc_timer_values(time.time() - start))
    writecsv.close()


def split_pdf(pdf_name):
    print("\033[92m\033[1mCropping PDFs & Template matching.\033[0m\n")
    start = time.time()
    with open(pdf_name, "rb") as in_f:
        log_input = PdfFileReader(in_f)
        numPages = log_input.getNumPages()
        x1, y1, x2, y2 = log_input.getPage(0).mediaBox
        # print("Document has %s page(s) of dimensions %s X %s." % (numPages, int(x2 - x1), int(y2 - y1)))
        '''
        # Crop off the lithology column
        litho_log_output = PdfFileWriter()
        for i in range(numPages):
            litho_log = log_input.getPage(i)
            litho_log.mediaBox.lowerLeft = (185, y2)
            litho_log.mediaBox.upperRight = (125, y1)
            litho_log_output.addPage(litho_log)

        with open((os.path.join(os.path.dirname(fil_name), "litho_log.pdf")), "wb") as out_f:
            litho_log_output.write(out_f)
        out_f.close()
        out_f = (os.path.join(os.path.dirname(fil_name), "litho_log.pdf"))
        convert(out_f, 600)
        
        # Crop off the surfaces column
        surface_log_ouput = PdfFileWriter()
        for i in range(numPages):
            surface_log = log_input.getPage(i)
            surface_log.mediaBox.lowerLeft = (375, y2)
            surface_log.mediaBox.upperRight = (350, y1)
            surface_log_ouput.addPage(surface_log)

        with open((os.path.join(os.path.dirname(fil_name), "surface_log.pdf")), "wb") as out_f:
            surface_log_ouput.write(out_f)
        out_f.close()
        out_f = (os.path.join(os.path.dirname(fil_name), "surface_log.pdf"))
        convert(out_f, 600)
        '''
        # # Crop off the sedimentary column
        sed_struc_log_output = PdfFileWriter()
        for i in range(numPages):
            sed_struc_log = log_input.getPage(i)
            sed_struc_log.mediaBox.lowerLeft = (240, y2)
            sed_struc_log.mediaBox.upperRight = (180, y1)
            sed_struc_log_output.addPage(sed_struc_log)

        with open((os.path.join(os.path.dirname(fil_name), "sed_struc_log.pdf")), "wb") as out_f:
            sed_struc_log_output.write(out_f)
        out_f.close()
        out_f = (os.path.join(os.path.dirname(fil_name), "sed_struc_log.pdf"))
        convert(out_f, 600)
        cropped_pdf_image = (os.path.join(os.path.dirname(fil_name), "sed_struc_log_python_convert.png"))
        template_folder = os.path.join((os.path.dirname(fil_name)), "templates", "sediments")
        matching(cropped_pdf_image, template_folder, 0.7)

        # Crop off the environment column
        env_log_ouput = PdfFileWriter()
        for i in range(numPages):
            env_log = log_input.getPage(i)
            env_log.mediaBox.lowerLeft = (575, y2)
            env_log.mediaBox.upperRight = (522, y1)
            env_log_ouput.addPage(env_log)

        with open((os.path.join(os.path.dirname(fil_name), "env_log.pdf")), "wb") as out_f:
            env_log_ouput.write(out_f)
        out_f.close()
        out_f = (os.path.join(os.path.dirname(fil_name), "env_log.pdf"))
        convert(out_f, 600)
        cropped_pdf_image = (os.path.join(os.path.dirname(fil_name), "env_log_python_convert.png"))
        template_folder = os.path.join((os.path.dirname(fil_name)), "templates", "environment")
        matching(cropped_pdf_image, template_folder, 0.9)

    in_f.close()
    print ("\nCompleted Cropping PDFs & Template matching in : \033[1m%s\033[0m\n" % calc_timer_values(time.time() - start))


'''
TEMPLATE FOLDER
    # - Load folder that contains all the templates to be matched.
'''

def load_templates(template_folder):
    templates_folder =[]
    for root, path_dir, filenames in os.walk(template_folder):
        for filename in filenames:
            templates_folder.append(os.path.join(root, filename))
    return templates_folder

'''
MATCH IMAGE & DISPLAY RESULT
    # - Match the template to their respective locations within the image.
'''

def matching(fil_name, folder, threshold):
    start = time.time()
    matched = {}
    temp_locations = []
    print("Processing %s" % os.path.basename(folder).upper())

    # load_image(fil_name) # Load Image
    img_bgr = cv2.imread(os.path.abspath(fil_name)) # Read Image as RGB
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) # Convert Image to grayscale
    cv2.imwrite(os.path.join(os.path.dirname(fil_name), 'gray_image.png'), img_gray) # Write binary Image

    templates_folder = load_templates(folder) # Load Templates from Folder

    for count, name in enumerate(templates_folder):
        a, b, c = random.choice(range(0, 256)), random.choice(range(0, 256)), random.choice(range(0, 256))  # Random Color choice
        template = cv2.imread(os.path.abspath(name), 0) # Read Template Image as RGB
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        # threshold = 0.70
        loc = np.where(res >= threshold)
        remove = []
        for pt in zip(*loc[::-1]):
            temp_locations.append(pt)
        temp_locations = sorted(temp_locations, key=itemgetter(1,0))
        for i, j in zip(temp_locations, temp_locations[1:]):
            if ((j[0] ** 2 + j[1] ** 2) ** 0.5 - (i[0] ** 2 + i[1] ** 2) ** 0.5) < 2:
                remove.append(j)
        unique = list(set(temp_locations) - set(remove))
        unique = sorted(unique, key=itemgetter(1, 0))
        uniqe_loc = []
        for pt in unique:
            # print("unique", pt, (pt[0] ** 2 + pt[1] ** 2) ** 0.5)
            cv2.rectangle(img_bgr, pt, (pt[0] + w, pt[1] + h), [a,b ,c], 2)
            uniqe_loc.append(pt[1])
        matched[os.path.basename(name)] = uniqe_loc
        print("%s - %s\t has %s matches." % (os.path.basename(folder).upper(), os.path.basename(name), len(set(unique))))
        temp_locations, remove = [], []
    output_file_name = str(os.path.basename(folder)) + '_detected.png'
    print(output_file_name)
    cv2.imwrite(os.path.join(os.path.dirname(fil_name), output_file_name), img_bgr)
    print(matched)
    print ("\nCompleted in : \033[1m%s\033[0m\n" % calc_timer_values(time.time() - start))


# LOAD MODULE

if __name__ == "__main__":
    try:
        initial_processing()
        # matching()
        print ("\nTotal Execution time: \033[1m%s\033[0m\n" % calc_timer_values(time.time() - abs_start))
    except KeyboardInterrupt:
        exit("TERMINATED BY USER")
