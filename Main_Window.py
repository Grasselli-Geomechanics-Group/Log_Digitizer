# /////////////////////////////////////////////////////////////// #
# !python3.6
# -*- coding: utf-8 -*-
# Python Script initially created on 2019-04-11 
# Compiled by Aly @ Grasselli Geomechanics Group, UofT, 2019 
# Created using PyCharm 
# Current Version 01 - Dated Apr 11, 2019
# /////////////////////////////////////////////////////////////// #

# WAND ERROR!!
# https://stackoverflow.com/questions/52699608/wand-policy-error-error-constitute-c-readimage-412


import sys# import csv
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
#     defined_color_map.append(a)
#
# print(defined_color_map)
#
# print(litho_legend)

import os

'''
LOAD .py MODULES
'''


import image  # Load main processing script
# import pdf_file_info  # Load the PDF File info
import folder_structure  # Create a proper folder structure if the PDFs are all in one folder

Available_Units = ['meters', 'feet']
'''
Global Variables
'''


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


'''
GUI CLASS
- Divided into 2 Frames
    - Input houses USER required information. 
    - Status shows when execution starts. 
'''


class Core_GUI(Frame):

    def cb(self):
        if(self.alessandro_cutting_log_status.get()):
            self.v.set(1500)
            self.d1.set(250)
            self.d2.set(305)
        else:
            self.v.set(765)
            self.d1.set(40)
            self.d2.set(60)

    def __init__(self, master):

        Frame.__init__(self, master)
        # Setting up frames
        self.frame1 = Frame(master)
        self.frame1.pack()

        #Heading
        self.master = master
        master.title("Graphic Log Digitiser")

        self.input = Frame(master, borderwidth=5, relief=GROOVE)
        self.input.pack(anchor=CENTER, fill=BOTH)

        self.status = Frame(master, borderwidth=5, relief=GROOVE)
        self.status.pack(anchor=CENTER, fill=BOTH)

        self.label = Label(self.input, text="Graphic Log Digitiser", font='Helvetica 14 bold')
        self.label.grid(row=1, column=1, sticky=W)

        #Execution Buttons
        self.greet_button = Button(self.input, text="BATCH FOLDER", fg="red", command=self.batch_folder)
        self.greet_button.grid(row=2, column=1, sticky=W)

        self.close_button = Button(self.input, text="SINGLE FILE", command=self.single_file)
        self.close_button.grid(row=2, column=2, sticky=W)

        #Allow for the Folder structure option
        self.folder_structure_status = IntVar()
        self.folder_structure = Checkbutton(self.input, text="Enable Folder Structure", variable=self.folder_structure_status)
        self.folder_structure.grid(row=3, column=1, sticky=W)

        # Allow for the Alessando
        self.alessandro_cutting_log_status = IntVar()
        self.alessandro_cutting_log = Checkbutton(self.input, text="Cuttings Log",
                                            variable=self.alessandro_cutting_log_status, command=self.cb)
        self.alessandro_cutting_log.grid(row=3, column=2, sticky=W)

        #Predefined Pixel ID
        self.pixel_label = Label(self.input, text="Depth Pixel ID Range\tLeft")
        self.pixel_label.grid(row=4, column=1, sticky=W)

        self.d1 = IntVar()
        self.d1.set(40)
        self.d1_ID = Entry(self.input, textvariable=self.d1)
        # self.d1_ID.pack(side=LEFT)
        self.d1_ID.grid(row=4, column=2, sticky=W)

        #Predefined Pixel ID
        self.pixel_label = Label(self.input, text="\t\t\tRight")
        self.pixel_label.grid(row=5, column=1, sticky=W)

        self.d2 = IntVar()
        self.d2.set(60)
        self.d2_ID = Entry(self.input, textvariable=self.d2)
        # self.d2_ID.pack(side=LEFT)
        self.d2_ID.grid(row=5, column=2, sticky=W)

        #Predefined Pixel ID
        self.pixel_label = Label(self.input, text="Lithology Pixel ID")
        self.pixel_label.grid(row=6, column=1, sticky=W)

        self.v = IntVar()
        self.v.set(765)
        self.pixel_ID = Entry(self.input, textvariable=self.v)
        self.pixel_ID.grid(row=6, column=2, sticky=W)

        #Predefined Precision
        self.LAS_precision = Label(self.input, text="Resolution")
        self.LAS_precision.grid(row=7, column=1, sticky=W)

        self.v1 = DoubleVar()
        self.v1.set(0.1)
        self.LAS_precision_int = Entry(self.input, textvariable=self.v1)
        self.LAS_precision_int.grid(row=7, column=2, sticky=W)

        #Predefined Pixel ID
        self.temp_match_label = Label(self.input, text="Template Match ID Range\tLeft")
        self.temp_match_label.grid(row=8, column=1, sticky=W)

        self.temp_matchd1 = IntVar()
        self.temp_matchd1.set(190)
        self.temp_matchd1_ID = Entry(self.input, textvariable=self.temp_matchd1)
        # self.d1_ID.pack(side=LEFT)
        self.temp_matchd1_ID.grid(row=8, column=2, sticky=W)

        #Predefined Pixel ID
        self.temp_match_label = Label(self.input, text="\t\t\tRight")
        self.temp_match_label.grid(row=9, column=1, sticky=W)

        self.temp_matchd2 = IntVar()
        self.temp_matchd2.set(240)
        self.temp_matchd2_ID = Entry(self.input, textvariable=self.temp_matchd2)
        # self.d2_ID.pack(side=LEFT)
        self.temp_matchd2_ID.grid(row=9, column=2, sticky=W)

        #Predefined Precision (Units of measure)
        self.LAS_unit = Label(self.input, text="Units")
        self.LAS_unit.grid(row=10, column=1, sticky=W)

        self.LASunits = StringVar()
        self.LASunits.set('meters')
        self.LAS_precision_unit = OptionMenu(self.input, self.LASunits, *Available_Units)
        self.LAS_precision_unit.grid(row=10, column=2, sticky=W)

        self.deb_status = IntVar()
        self.debug_mode_status = Checkbutton(self.input, text="Enable Debugging", variable=self.deb_status)
        self.debug_mode_status.grid(row=11, column=1, sticky=W)

        self.organizing_grid()

    def organizing_grid(self):
        for x in range(0, 1):
            self.input.grid_columnconfigure(x, weight=1, uniform='a')
            self.status.grid_columnconfigure(x, weight=1, uniform='a')

    def gui_update(self):
        # UPDATE GUI
        self.state = Label(self.status, text="WORKING...", font=(None, 8))
        self.state.grid(row=1, column=1, sticky=W)
        self.update()

    def single_file(self):
        # show an "Open" dialog box and return the path to the selected file
        filename = askopenfilename(filetypes=[("PDF files", ("*.pdf", "*.PDF"))])

        # UPDATE GUI
        self.gui_update()

        # Check debugging
        image.debugging_mode(self.deb_status.get())

        # Check debugging
        image.cuttings_mode(self.alessandro_cutting_log_status.get())

        # Check for folder structure
        if self.folder_structure_status.get() == 1:
            folder_structure.create_sub_directories(os.path.abspath(filename))

        # Execute image.py
        if filename:
            image.open_file(filename, self.v.get(), self.v1.get(), self.d1.get(), self.d2.get(), self.temp_matchd1_ID.get(), self.temp_matchd2_ID.get(), self.LASunits.get())
            image.processing_complete()

        root.destroy()

    def batch_folder(self):
        # show an "Open" dialog box and return the path to the selected folder
        filename = askdirectory()

        # UPDATE GUI
        self.gui_update()

        # Check debugging
        image.debugging_mode(self.deb_status.get())

        # Check debugging
        image.cuttings_mode(self.alessandro_cutting_log_status.get())

        # Check for folder structure
        if self.folder_structure_status.get() == 1:
            folder_structure.create_sub_directories(os.path.abspath(filename))

        # Execute image.py
        if filename:
            print('\nBatch processing...\n')
            directories = image.findSubdirectories(os.path.abspath(filename))

            # Loop over directory(ies)
            # Loop over directory(ies)
            # if directories is not None and directories:
            for sub_dir in directories:
                files = [f for f in os.listdir(sub_dir)]
                for filename in files:
                    if filename.endswith('.pdf'):
                        full_fname = os.path.join(sub_dir, filename)
                        image.open_file(full_fname, self.v.get(), self.v1.get(), self.d1.get(), self.d2.get(),
                                        self.temp_matchd1_ID.get(), self.temp_matchd2_ID.get(), self.LASunits.get())
        image.processing_complete()

        root.destroy()


if __name__ == "__main__":
    try:
        root = Tk()
        core_interpreter_gui = Core_GUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        exit("TERMINATED BY USER")