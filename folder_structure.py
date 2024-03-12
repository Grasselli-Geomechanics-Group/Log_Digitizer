###
# Script that creates a predefined folder structure based on the filenames being passed.
# It also creates the templates folder and moves the predefined images in the "templates" folder of the script.
###

import os
import shutil


def create_folder(dir_path, sub_dir_name):
    """
    Creates folder based on the file name (i.e, sub_dir_name)

    :param dir_path: Name of directory
    :type dir_path: str
    :param sub_dir_name: Name of subdirectory
    :type sub_dir_name: str

    :return: name of the newly created folder
    :rtype: str
    """

    folder_name_to_check = os.path.join(dir_path, sub_dir_name)
    if not os.path.exists(folder_name_to_check):  # Check to see if the folder exists
        os.makedirs(folder_name_to_check)  # if not then makes the folder
    return folder_name_to_check


def create_sub_directories(root_dir, file_ext='.pdf', single_file_status = False):
    """
    Iterates through the PDF files, when in Batch Mode, to create the predefined folder structure.
    In Single file mode, it will just return the new file path after creating the predefined folder structure.

    :param root_dir: Name of the main directory
    :type root_dir: str
    :param file_ext: Look for files ending with file extension
    :type file_ext: str
    :param single_file_status: expects this argument to be passed a folder (Batch Mode), but can be passed as PDF in the single file mode
    :type single_file_status: bool

    :return: new file path for a single file after being inserted in the new folder structure
    :rtype: str
    """

    if os.path.isfile(root_dir):
        print("Selected file will be defined a Folder Structure")
        single_file_status = True
        root_dir = (os.path.dirname(root_dir))  # Get the folder name where the file lives.

    for directory, subdirectories, files in os.walk(root_dir):
        for file in files:
            if file.endswith(file_ext):  # Look for files ending with PDF
                fil_name = (os.path.splitext(file)[0])  # Get file name without extension
                name_of_new_folder = create_folder(directory, fil_name)  # Create directory

                # Move PDF to the new directory
                os.rename(os.path.join(directory, file), os.path.join(name_of_new_folder, file))

                # Create the templates folder in the new directory
                template_folder = create_folder(name_of_new_folder, "templates")
                for _, _, fils in os.walk("templates"):
                    for i in fils:
                        shutil.copy(os.path.join("templates", i), template_folder)

                if single_file_status:
                    new_dirpath = os.path.join(root_dir, fil_name, (fil_name + os.path.splitext(file)[1]))
                    return new_dirpath


if __name__ == "__main__":
    try:
        create_sub_directories('/home/aly/Desktop/20220525_Stav/Logs', file_ext='.xlsx')
    except KeyboardInterrupt:
        exit("TERMINATED BY USER")
#
