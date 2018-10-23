# /////////////////////////////////////////////////////////////// #
# Python Script initially created on 22/10/18 
# Compiled by Aly @ Grasselli Geomechanics Group, UofT, 2018 
# Created using PyCharm 
# /////////////////////////////////////////////////////////////// #

import os, shutil

# /// Create post_processing folder /// #

def create_post_processing(dir_path, sub_dir_name):
    global post_processing
    post_processing = os.path.join((dir_path), sub_dir_name)
    # print post_processing
    if not os.path.exists(post_processing): # Check to see if the folder exists
        os.makedirs(post_processing) # if not then makes the folder
    return post_processing

def create_sub_directories(root_dir):
    for directory, subdirectories, files in os.walk(root_dir):
        for file in files:
            # print(directory,file)
            fil_name = (os.path.splitext(file)[0])
            # print os.path.join(directory, file)
            create_post_processing(directory, fil_name)
            os.rename(os.path.join(directory, file), os.path.join(post_processing, file))
            template_folder = os.path.join(post_processing, "templates")
            if not os.path.exists(template_folder):  # Check to see if the folder exists
                os.makedirs(template_folder)  # if not then makes the folder
            for dir, subdir, fils in os.walk("templates"):
                for i in fils:
                    shutil.copy(os.path.join("templates", i), template_folder)

create_sub_directories('/home/aly/Desktop/Progress_log_pdfs')