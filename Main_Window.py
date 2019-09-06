# /////////////////////////////////////////////////////////////// #
# !python3.6
# -*- coding: utf-8 -*-
# Python Script initially created on 2019-04-11 
# Compiled by Aly @ Grasselli Geomechanics Group, UofT, 2019 
# Created using PyCharm 
# Current Version 01 - Dated Apr 11, 2019
# /////////////////////////////////////////////////////////////// #

import sys
import os

'''
LOAD .py MODULES
'''


import image  # Load main processing script
# import pdf_file_info  # Load the PDF File info
import folder_structure  # Create a proper folder structure if the PDFs are all in one folder

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
    def __init__(self, master):

        Frame.__init__(self, master)
        # Setting up frames
        self.frame1 = Frame(master)
        self.frame1.pack()

        #Heading
        self.master = master
        master.title("Core Log Interpreter")

        self.input = Frame(master, borderwidth=5, relief=GROOVE)
        self.input.pack(anchor=CENTER, fill=BOTH)

        self.status = Frame(master, borderwidth=5, relief=GROOVE)
        self.status.pack(anchor=CENTER, fill=BOTH)

        self.label = Label(self.input, text="Core Log Interpreter", font='Helvetica 14 bold')
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

        #Predefined Pixel ID
        self.pixel_label = Label(self.input, text="Pixel ID")
        self.pixel_label.grid(row=4, column=1, sticky=W)

        self.v = IntVar()
        self.v.set(765)
        self.pixel_ID = Entry(self.input, textvariable=self.v)
        self.pixel_ID.grid(row=4, column=2, sticky=W)

        #Predefined Precision
        self.LAS_precision = Label(self.input, text="Precision")
        self.LAS_precision.grid(row=5, column=1, sticky=W)

        self.v1 = DoubleVar()
        self.v1.set(0.1)
        self.LAS_precision_int = Entry(self.input, textvariable=self.v1)
        self.LAS_precision_int.grid(row=5, column=2, sticky=W)

        self.deb_status = IntVar()
        self.debug_mode_status = Checkbutton(self.input, text="Enable Debugging", variable=self.deb_status)
        self.debug_mode_status.grid(row=6, column=1, sticky=W)

        self.organizing_grid()

    def organizing_grid(self):
        for x in range(0, 1):
            self.input.grid_columnconfigure(x, weight=1, uniform='a')
            self.status.grid_columnconfigure(x, weight=1, uniform='a')

    def single_file(self):
        # show an "Open" dialog box and return the path to the selected file
        filename = askopenfilename(filetypes=[("PDF files", ("*.pdf", "*.PDF"))])

        # UPDATE GUI
        self.state = Label(self.status, text="WORKING...", font=(None, 8))
        self.state.grid(row=1, column=1, sticky=W)
        self.update()

        # Check debugging
        image.debugging_mode(self.deb_status.get())

        # Check for folder structure
        if self.folder_structure_status.get() == 1:
            folder_structure.create_sub_directories(os.path.abspath(filename))

        # Execute image.py
        if filename:
            image.open_file(filename, self.v.get(), self.v1.get())
            image.processing_complete()

        root.destroy()

    def batch_folder(self):
        # show an "Open" dialog box and return the path to the selected folder
        filename = askdirectory()

        # UPDATE GUI
        self.state = Label(self.status, text="WORKING...", font=(None, 8))
        self.state.grid(row=1, column=1, sticky=W)
        self.update()

        # Check debugging
        image.debugging_mode(self.deb_status.get())

        # Check for folder structure
        if self.folder_structure_status.get() == 1:
            folder_structure.create_sub_directories(os.path.abspath(filename))

        # Execute image.py
        if filename:
            print('\nBatch processing...\n')
            directories = image.findSubdirectories(os.path.abspath(filename))
            # Loop over directory(ies)
            if directories is not None and directories:
                for sub_dir in directories:
                    image.open_file(sub_dir, self.v.get(), self.v1.get())
                image.processing_complete()

        root.destroy()


if __name__ == "__main__":
    try:
        root = Tk()
        core_interpreter_gui = Core_GUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        exit("TERMINATED BY USER")