import csv
import webcolors

defined_color_map = []
rg_list = []
new_list = []
litho_csv = "litho_legend.csv"
color_csv = "defined_color_map.csv"
with open(litho_csv, mode='r') as infile:
    reader = csv.reader(infile)
    litho_legend = {rows[0]:rows[1] for rows in reader}
    b = webcolors.name_to_rgb(rows[0] for rows in reader)[0], webcolors.name_to_rgb(rows[0] for rows in reader)[1], webcolors.name_to_rgb(rows[0] for rows in reader)[2]
    print(b)
    # defined_color_map.append(a)
infile.close()
for key in litho_legend:
    a = webcolors.name_to_rgb(key)[0], webcolors.name_to_rgb(key)[1], webcolors.name_to_rgb(key)[2]
    defined_color_map.append(a)
#     # print(a)
#     # print(key, webcolors.name_to_rgb(key)[0], webcolors.name_to_rgb(key)[1], webcolors.name_to_rgb(key)[2])
#     # print(get_colour_name(i))
print(defined_color_map)

# with open(color_csv, mode='r') as infile:
#     reader = csv.DictReader(infile)
#     for row in reader:
#         defined_color_map.append((int(row["R"]), int(row["G"]), int(row["B"])))
# infile.close()

# print(defined_color_map)
print(litho_legend)


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
