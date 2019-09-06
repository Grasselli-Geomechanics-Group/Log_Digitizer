# import csv
# import webcolors
#
# defined_color_map = []
# rg_list = []
# new_list = []
# litho_csv = "litho_legend.csv"
# color_csv = "defined_color_map.csv"
# with open(litho_csv, mode='r') as infile:
#     reader = csv.reader(infile)
#     litho_legend = {rows[0]:rows[1] for rows in reader}
#     b = webcolors.name_to_rgb(rows[0] for rows in reader)[0], webcolors.name_to_rgb(rows[0] for rows in reader)[1], webcolors.name_to_rgb(rows[0] for rows in reader)[2]
#     print(b)
# infile.close()
#
# for key in litho_legend:
#     a = webcolors.name_to_rgb(key)[0], webcolors.name_to_rgb(key)[1], webcolors.name_to_rgb(key)[2]
#     litho_legend.csv.append(a)
#
# print(defined_color_map)
#
# print(litho_legend)

