# /////////////////////////////////////////////////////////////// #
# !python2.7
# -*- coding: utf-8 -*-
# Python Script initially created on 12/05/2018
# Compiled by Aly @ Grasselli's Geomechanics Group, UofT, 2018
# Created using PyCharm // Tested on Spyder
# Current Version 01 - Dated May 13, 2018
# /////////////////////////////////////////////////////////////// #

## This code was compiled based on the layout of d_66_I_94_B_16_Continuous_Core Log

from PIL import Image
import time, os, webcolors, csv
from collections import Counter

start = time.time()

'''
COMPILING VARIABLES AND USER INPUTS
    # Required User Inputs
        # - No. of unique colors
        # - Excluded colors from mapping
        # - Two points on log with their depth and pixel location
'''
## Variables
color_map = []
defined_color_map = []
defined_number_of_unique_colors = 6
top_of_log = 793  # top of lithology bar on a 300dpi @ Pixel 793
excluded_colors = [(255, 255, 255), (36, 31, 33)]  # exclusion colors from mapping [(White), (Black)]
fil_name = 'E:/Dropbox/Python_Codes/Progress_BHLOG/d_66_I_94_B_16_Continuous_Core-1.png'

## LEGEND DICTIONARY
legend = {"skyblue":"Laminated Bedded Resedimented Bioclasts", "sandybrown":"Bituminous F-C Siltstone", "tan":"Bituminous F-M Siltstone", "khaki":"Sandy F-C Siltstone to Silty VF Sandstone", "darkseagreen": "Phosphatic - Bituminous Sandy Siltstone to Breccia", "plum":"Calcareous - Calcispheric Dolosiltstone"}

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
        return ("\033[1m%.2f seconds\033[0m" % end_time)
    else:
        return ("\033[1m%d minutes and %d seconds\033[0m." % (minutes, sec))

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
INITIALISATION
    # - Loads Image
    # - Obtains all colors (1 pixel wide) at X location
    # - Reduces colors to an amount equal to the user defined unique colors
'''


def initial_processing(file_name, defined_number_of_unique_colors):
    # Load Image
    im = Image.open(file_name)
    # Convert to RGB
    rgb_im = im.convert('RGB')
    # Obtain image dimension for digitization
    width, height = im.size
    # Approximate Locations on Image for Lithological Identification
    x_approx_litho = int((775./2550) * width)  # on a 300dpi @ Pixel 775
    y_start_approx_litho = int((float(top_of_log)/21300) * height)
    y_end_approx_litho = int((21178./21300) * height)  # on a 300dpi @ Pixel 21178

    # Obtain All Colors (1 Color/pixel) in the Lithological Identification
    for j in range(y_start_approx_litho, y_end_approx_litho):
        r, g, b = rgb_im.getpixel((x_approx_litho, j))
        color_map.append(rgb_im.getpixel((x_approx_litho, j)))

    print("No. of existing colors in log: %s" % len(set(color_map)))
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
    counter = 0
    for i in range(1, len(color_map)):
        if color_map[i] not in unique_color_map:
            color_map[i] = color_map[i - 1]
            counter += 1

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
    # location.append(i)
    for h, m in enumerate(location):
        color_map[m] = color_map[min(location) - 1]

    color_map.pop()

    ## MOVE TO NEXT MODULE - DIGITIZE LOG
    digitized_log(color_map)


'''
DIGITIZE LOG
    # - Returns depth based on pixel location as defined by user
    # - Returns stratigraphical sequence (Based on color)
'''


def digitized_log(color_map):
    ch_top = []
    output_file = os.path.dirname(fil_name) + "/stratigraphical_sequence.csv"
    with open(output_file, 'w') as writecsv:
        writer = csv.writer(writecsv)
        writer.writerow(["From (m)", "To (m)", "Color Code", "Lithofacies"])
        for i, j in enumerate(color_map):
            # if i in range(15000, 16000):
            if i < (len(color_map) - 1):
                ch_top.append(round((depth[0] + ((i + top_of_log - pixel_id[0]) / ratio)), 3))
                if color_map[i] != color_map[i + 1]:
                    ch = (round((depth[0] + ((i + top_of_log - pixel_id[0]) / ratio)), 3))
                    writer.writerow(["{0:.3f}".format(min(ch_top)), "{0:.3f}".format(ch), get_colour_name(j)[1], legend.get(get_colour_name(j)[1])])
                    ch_top = []

    print ("\nCompleted in : \033[1m%s\033[0m" % calc_timer_values(time.time() - start))
    writecsv.close()

# LOAD MODULE
initial_processing(fil_name, defined_number_of_unique_colors)
