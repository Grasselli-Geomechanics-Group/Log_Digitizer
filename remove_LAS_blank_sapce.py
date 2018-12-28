# /////////////////////////////////////////////////////////////// #
# Python Script initially created on 11/12/18 
# Compiled by Aly @ Grasselli Geomechanics Group, UofT, 2018 
# Created using PyCharm 
# /////////////////////////////////////////////////////////////// #

import csv, os

dir_path = "/home/aly/Desktop/Progress_Energy/CSV"
sub_dir_name = "processed"
post_processing = os.path.join(dir_path, sub_dir_name)
for root, dirs, files in os.walk(dir_path):
    for filename in files:
        with open(os.path.join(dir_path, filename), 'r') as readcsv, open(os.path.join(post_processing, filename), 'w') as out:
            # print(os.path.join(dir_path, filename), os.path.join(post_processing, filename))
            writer = csv.writer(out)
            for row in csv.reader(readcsv):
                if row[2] != "Blank Space":

                    writer.writerow(row)
                else:
                    print(os.path.join(dir_path, filename), "BLANK FOUND")
        readcsv.close()
        out.close()