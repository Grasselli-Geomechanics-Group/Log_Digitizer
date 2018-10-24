# /////////////////////////////////////////////////////////////// #
# !python3.6
# -*- coding: utf-8 -*-
# Python Script initially created on 22/10/18 
# Compiled by Aly @ Grasselli Geomechanics Group, UofT, 2018 
# Created using PyCharm 
# /////////////////////////////////////////////////////////////// #

# SCRIPT PUTS EVERY PDF IN A FOLDER #
# FOLDER NAME IS THE SAME AS THE PDF #
import os
import shutil

# /// Create folder /// #
'''
Requires
    - Directory Path
    - Name of sub-folder to create
'''


def create_folder(dir_path, sub_dir_name):
    global post_processing
    post_processing = os.path.join(dir_path, sub_dir_name)
    if not os.path.exists(post_processing):  # Check to see if the folder exists
        os.makedirs(post_processing)  # if not then makes the folder
    return post_processing


# /// Create Structure of Sub Directories /// #
'''
Requires
    - Name of root folder
'''


def create_sub_directories(root_dir):
    for directory, subdirectories, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.pdf'):  # Look for files ending with PDF
                fil_name = (os.path.splitext(file)[0])  # Get file name without extension
                create_folder(directory, fil_name)  # Create directory
                # Move PDF to the new directory
                os.rename(os.path.join(directory, file), os.path.join(post_processing, file))
                template_folder = os.path.join(post_processing, "templates")
                if not os.path.exists(template_folder):  # Check to see if the folder exists
                    os.makedirs(template_folder)  # if not then makes the folder
                # Make an instance of the templates folder into the newly created folder.
                for _, _, fils in os.walk("templates"):
                    for i in fils:
                        shutil.copy(os.path.join("templates", i), template_folder)


create_sub_directories('/home/aly/Desktop/Progress_log_pdfs')
