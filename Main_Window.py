# /////////////////////////////////////////////////////////////// #
# !python3.6
# -*- coding: utf-8 -*-
# Python Script initially created on 2019-04-11 
# Compiled by Aly @ Grasselli Geomechanics Group, UofT, 2019 
# Created using PyCharm 
# Current Version 01 - Dated Apr 11, 2019
# /////////////////////////////////////////////////////////////// #

# TODO:
#  1- The status update window does not update properly. It writes over the previous text.
#  2- If you run the same file back.to.back it will flag an error. Possibly it inherits some depth variable from the previous file. Error is here   File "E:\Dropbox\Python_Codes\Log_Digitizer\log_digitizer.py", line 552, in log_info
#     if k1.count("_") > 1:

import sys
import os

import log_digitizer  # Load main processing script
# import pdf_file_info  # Load the PDF File info
import folder_structure  # Create a proper folder structure if the PDFs are all in one folder


'''
Global Variables
'''


Available_Units = ['meters', 'feet']
global filename
global debug_mode


'''
Tkinter Check
- Check the Python Version for compatibility. 
'''


ver = sys.version
if ver[0] == str(2):
    exit("\nSCRIPT ONLY WORKS ON PYTHON 3\n")
    # from Tkinter import *
    # from Tkinter import filedialog
    # from tkinter.filedialog import askopenfilename, askdirectory
else:
    from tkinter import *
    # from tkinter import filedialog
    from tkinter.filedialog import askopenfilename, askdirectory


class Core_GUI(Frame):
    """
    GUI CLASS
    - Divided into 2 Frames
        - Input houses USER required information.
        - Status shows when execution starts.
    """

    def process_cutting_log(self):
        """
        Default settings for
        - Cutting Log created by Alessandro Terzuoli
        - Petrographic Logs created by Thomas F. Moslow
        :return:
        """

        if self.alessandro_cutting_log_status.get():
            self.pixel_ID_default.set(1500)
            self.depth_pixel_left_default.set(250)
            self.depth_pixel_right_default.set(305)
        else:
            self.pixel_ID_default.set(765)
            self.depth_pixel_left_default.set(40)
            self.depth_pixel_right_default.set(60)
        return self.LAS_precision_int_default, self.depth_pixel_left_default, self.depth_pixel_right_default

    def __init__(self, master):

        Frame.__init__(self, master)
        # Setting up frames
        self.frame1 = Frame(master)
        self.frame1.pack()

        # Heading
        self.master = master
        master.title("Graphic Log Digitiser")

        self.input = Frame(master, borderwidth=5, relief=GROOVE)
        self.input.pack(anchor=CENTER, fill=BOTH)

        self.status = Frame(master, borderwidth=5, relief=GROOVE)
        self.status.pack(anchor=CENTER, fill=BOTH)

        self.label = Label(self.input, text="Graphic Log Digitiser", font='Helvetica 14 bold')
        self.label.grid(row=1, column=1, sticky=W)

        # Execution Buttons
        self.greet_button = Button(self.input, text="BATCH FOLDER", fg="red", command=self.batch_folder)
        self.greet_button.grid(row=2, column=1, sticky=W)

        self.close_button = Button(self.input, text="SINGLE FILE", command=self.single_file)
        self.close_button.grid(row=2, column=2, sticky=W)

        # Allow for the Folder structure option
        self.folder_structure_status = IntVar()
        self.folder_structure = Checkbutton(self.input, text="Enable Folder Structure", variable=self.folder_structure_status)
        self.folder_structure.grid(row=3, column=1, sticky=W)

        # Allow for the Alessando (Cuttings Logs)
        self.alessandro_cutting_log_status = BooleanVar()
        self.alessandro_cutting_log = Checkbutton(self.input, text="Cuttings Log",
                                                  variable=self.alessandro_cutting_log_status, command=self.process_cutting_log)
        self.alessandro_cutting_log.grid(row=3, column=2, sticky=W)

        # Predefined Pixel ID - Depth (Left)
        self.pixel_label = Label(self.input, text="Extent of Depth Column\t\tLeft")
        self.pixel_label.grid(row=4, column=1, sticky=W)

        self.depth_pixel_left_default = IntVar()
        self.depth_pixel_left_default.set(40)
        self.depth_pixel_left = Entry(self.input, textvariable=self.depth_pixel_left_default)
        self.depth_pixel_left.grid(row=4, column=2, sticky=W)

        # Predefined Pixel ID - Depth (Right)
        self.pixel_label = Label(self.input, text="\t\t\t\tRight")
        self.pixel_label.grid(row=5, column=1, sticky=W)

        self.depth_pixel_right_default = IntVar()
        self.depth_pixel_right_default.set(60)
        self.depth_pixel_right = Entry(self.input, textvariable=self.depth_pixel_right_default)
        self.depth_pixel_right.grid(row=5, column=2, sticky=W)

        # Predefined Pixel ID - Template (Left)
        self.temp_match_label = Label(self.input, text="Extent of Template Match Column\tLeft")
        self.temp_match_label.grid(row=6, column=1, sticky=W)

        self.temp_matchd1 = IntVar()
        self.temp_matchd1.set(190)
        self.temp_matchd1_ID = Entry(self.input, textvariable=self.temp_matchd1)
        self.temp_matchd1_ID.grid(row=6, column=2, sticky=W)

        # Predefined Pixel ID - Template (Right)
        self.temp_match_label = Label(self.input, text="\t\t\t\tRight")
        self.temp_match_label.grid(row=7, column=1, sticky=W)

        self.temp_matchd2 = IntVar()
        self.temp_matchd2.set(240)
        self.temp_matchd2_ID = Entry(self.input, textvariable=self.temp_matchd2)
        self.temp_matchd2_ID.grid(row=7, column=2, sticky=W)

        # Predefined Pixel ID - Lithology
        self.pixel_label = Label(self.input, text="Lithology Pixel ID")
        self.pixel_label.grid(row=8, column=1, sticky=W)

        self.pixel_ID_default = IntVar()
        self.pixel_ID_default.set(765)
        self.pixel_ID = Entry(self.input, textvariable=self.pixel_ID_default)
        self.pixel_ID.grid(row=8, column=2, sticky=W)

        # Predefined Precision - Resolution
        self.LAS_precision = Label(self.input, text="Resolution")
        self.LAS_precision.grid(row=9, column=1, sticky=W)

        self.LAS_precision_int_default = DoubleVar()
        self.LAS_precision_int_default.set(0.1)
        self.LAS_precision_int = Entry(self.input, textvariable=self.LAS_precision_int_default)
        self.LAS_precision_int.grid(row=9, column=2, sticky=W)

        # Predefined Precision (Units of measure)
        self.LAS_unit = Label(self.input, text="Units")
        self.LAS_unit.grid(row=10, column=1, sticky=W)

        self.LAS_unit_default = StringVar()
        self.LAS_unit_default.set('meters')
        self.LAS_precision_unit = OptionMenu(self.input, self.LAS_unit_default, *Available_Units)
        self.LAS_precision_unit.grid(row=10, column=2, sticky=W)

        self.deb_status = BooleanVar()
        self.debug_mode_status = Checkbutton(self.input, text="Enable Debugging", variable=self.deb_status)
        self.debug_mode_status.grid(row=11, column=1, sticky=W)

        self.organizing_grid()

    def organizing_grid(self):
        for x in range(0, 1):
            self.input.grid_columnconfigure(x, weight=1, uniform='a')
            self.status.grid_columnconfigure(x, weight=1, uniform='a')

    def gui_update(self, update_text="WORKING...", clear_label=False):
        # UPDATE GUI
        self.state = Label(self.status, font=(None, 8))
        self.state.configure(text=update_text)
        self.state.grid(row=1, column=1, sticky=W)
        self.update()

    def single_file(self):
        """
        Show an "Open" dialog box and return the path to the selected file.
        If the file structure is enabled, the PDF file will be moved to a folder with the same name as the file.
        The script will then initiate the running the remainder of the python modules.

        :return:
        """

        filename = askopenfilename(filetypes=[("PDF files", ("*.pdf", "*.PDF"))])


        if filename:
            # UPDATE GUI
            self.gui_update(clear_label=True)

            # Check for folder structure
            if self.folder_structure_status.get() == 1:
                filename = folder_structure.create_sub_directories(os.path.abspath(filename))

            log_digitizer.open_file(filename, self.pixel_ID_default.get(), self.LAS_precision_int_default.get(), self.depth_pixel_left_default.get(), self.depth_pixel_right_default.get(), self.temp_matchd1_ID.get(), self.temp_matchd2_ID.get(), self.LAS_unit_default.get(), self.alessandro_cutting_log_status.get(), self.deb_status.get())
            log_digitizer.processing_complete()

            self.gui_update(update_text='Processed successfully')

        else:
            self.gui_update(update_text='filePath is not contain path')


    def batch_folder(self):
        # show an "Open" dialog box and return the path to the selected folder
        filename = askdirectory()

        # UPDATE GUI
        self.gui_update(clear_label=True)

        # # Check debugging
        # log_digitizer.debugging_mode(self.deb_status.get())
        #
        # # Check for log type default variables
        # log_digitizer.cuttings_logs_mode(self.alessandro_cutting_log_status.get())

        # Execute log_digitizer.py
        if filename:

            # Check for folder structure
            if self.folder_structure_status.get() == 1:
                folder_structure.create_sub_directories(os.path.abspath(filename))

            print('\nBatch processing...\n')
            directories = log_digitizer.findSubdirectories(os.path.abspath(filename))

            # Loop over directory(ies)
            for sub_dir in directories:
                files = [f for f in os.listdir(sub_dir)]
                for filename in files:
                    if filename.endswith('.pdf'):
                        full_fname = os.path.join(sub_dir, filename)
                        log_digitizer.open_file(full_fname, self.pixel_ID_default.get(), self.LAS_precision_int_default.get(), self.depth_pixel_left_default.get(), self.depth_pixel_right_default.get(),
                                        self.temp_matchd1_ID.get(), self.temp_matchd2_ID.get(), self.LAS_unit_default.get(), self.alessandro_cutting_log_status.get()), self.deb_status.get()
        log_digitizer.processing_complete()

        root.destroy()


if __name__ == "__main__":
    try:
        root = Tk()
        core_interpreter_gui = Core_GUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        exit("TERMINATED BY USER")