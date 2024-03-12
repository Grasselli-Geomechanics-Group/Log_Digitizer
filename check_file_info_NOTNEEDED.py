# /////////////////////////////////////////////////////////////// #
# !python2.7
# -*- coding: utf-8 -*-
# Python Script initially created on 03/03/19 
# Compiled by Aly @ Grasselli Geomechanics Group, UofT, 2019 
# Created using PyCharm 
# Current Version - Dated Apr 23, 2018
# /////////////////////////////////////////////////////////////// #

import time


def calc_timer_values(end_time):
    """
    Calculates the time taken to execute the function. Converts the seconds into minutes and seconds.

    :param end_time: the time needed to execute the function.
    :type end_time: float
    :return: the end time in seconds format OR minute and second format.
    """

    minutes, sec = divmod(end_time, 60)
    if end_time < 60:
        return ("\033[1m%.2f seconds\033[0m" % end_time)
    else:
        return ("\033[1m%d minutes and %d seconds\033[0m." % (minutes, sec))


def red_text(val):
    """
    Returns text in RED BOLD text

    :param val: string to be converted.
    :type val: str
    :return: text in RED BOLD format.
    """
    tex = "\033[1;31m%s\033[0m" % val
    return tex


def green_text(val):
    """
    Returns text in GREEN BOLD text

    :param val: string to be converted.
    :type val: str
    :return: text in GREEN BOLD format.
    """
    tex = "\033[1;92m%s\033[0m" % val
    return tex


def bold_text(val):
    """
    Returns text in BOLD text

    :param val: string to be converted.
    :type val: str
    :return: text in BOLD format.
    """
    tex = "\033[1m%s\033[0m" % val
    return tex

# Records the start time of the script.
start = tot_start = time.time()

def walk(obj, fnt, emb):
    """
    If there is a key called 'BaseFont', that is a font that is used in the document.
    If there is a key called 'FontName' and another key in the same dictionary object that is called 'FontFilex' (where x is null, 2, or 3), then that fontname is embedded.

    We create and add to two sets, fnt = fonts used and emb = fonts embedded.

    :param obj: object
    :param fnt: fonts used
    :param emb: fonts embedded
    :return: return the sets for each page
    """

    if not hasattr(obj, 'keys'):
        return None, None
    fontkeys = set(['/FontFile', '/FontFile2', '/FontFile3'])
    if '/BaseFont' in obj:
        fnt.add(obj['/BaseFont'])
    if '/FontName' in obj:
        if [x for x in fontkeys if x in obj]:  # test to see if there is FontFile
            emb.add(obj['/FontName'])

    for k in obj.keys():
        walk(obj[k], fnt, emb)

    return fnt, emb

def main(dir_path):
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument
    from PyPDF2 import PdfFileReader

    import os

    sub_dirs = []
    for root, dirs, files in os.walk(dir_path):
        # for dir_name in dirs:
        for filename in files:
            if filename.endswith(('.pdf')):
                if filename != "sed_struc_log.pdf":
                    # print (os.path.join(root,name))
                    sub_dirs.append(os.path.join(root, filename))
                    # print (os.path.join(root,name))
                    # sub_dirs.append(os.path.join(root, dir_name, filename))
    sub_dirs = sorted(list(set(sub_dirs)))  # Sort directories alphabetically in ascending order
    print("Found \033[1m%s\033[0m sub-directories" % len(sub_dirs))

    pro_aut, pro_creat, pro_pro = [], [], []
    err_aut, err_creat, err_pro = [], [], []
    pro_list, err_list = [], []
    for i in sub_dirs:

        fp = open(i, 'rb')
        parser = PDFParser(fp)
        # doc = PDFDocument(parser)
        pdf_toread = PdfFileReader(open(i, "rb"))
        pdf_info = pdf_toread.getDocumentInfo()
        try:
            date = pdf_info['/CreationDate']
            Producer = pdf_info['/Producer']
            Creator = pdf_info['/Creator']
            Author = pdf_info['/Author']
        except KeyError:
            date = "Unknown"
            Author = "Unknown"
            Creator = "Unknown"
            Producer = "Unknown"
        if os.path.isfile(os.path.join(os.path.dirname(i), "sed_struc_log.pdf")):
            print(green_text("\nPROCESSED %s" % i))
            # print(green_text(doc.info))  # The "Info" metadata
            print(green_text("PDF Engines %s %s, Made by %s on %s" % (str(Producer), str(Creator), str(Author), str(date)[2:10])))
            pro_aut.append(str(Author))
            pro_creat.append(str(Creator))
            pro_pro.append(str(Producer))
            pro_list.append([str(Author), str(Creator), str(Producer)])
        else:
            print(red_text("\nERROR LOG %s" % i))
            # print(red_text(doc.info))  # The "Info" metadata
            print(red_text("PDF Engines %s %s, Made by %s on %s" % (str(Producer), str(Creator), str(Author), str(date)[2:10])))
            err_aut.append(str(Author))
            err_creat.append(str(Creator))
            err_pro.append(str(Producer))
            err_list.append([str(Author), str(Creator), str(Producer)])

        '''
        CHECK FONTS
        '''

        pdf = PdfFileReader(i)
        fonts = set()
        embedded = set()
        for page in pdf.pages:
            obj = page.getObject()
            f, e = walk(obj['/Resources'], fonts, embedded)
            fonts = fonts.union(f)
            embedded = embedded.union(e)

        unembedded = fonts - embedded
        print('Font List')
        if fonts:
            print(sorted(list(fonts)))
        else:
            print("No Fonts Found")
        if unembedded:
            print('\nUnembedded Fonts')


    print("Processed")
    # print(type(pro_list), pro_list,)
    # print(set(pro_aut), set(pro_creat), set(pro_pro))

    # pro_list_Set = set([tuple([tuple(sorted(image_dict.items())) for image_dict in inner_list]) for inner_list in pro_list])
    # err_list_Set = set([tuple([tuple(sorted(image_dict.items())) for image_dict in inner_list]) for inner_list in err_list])

    l_of_processed_files = []
    for i in pro_list:
        if i not in l_of_processed_files:
            l_of_processed_files.append(i)


    l_of_unprocessed_files = []
    for i in err_list:
        if i not in l_of_unprocessed_files:
            l_of_unprocessed_files.append(i)

    if l_of_unprocessed_files:
        print(red_text("File Not Processed"))
        print(l_of_unprocessed_files)
    else:
        print(green_text("All Files Processed"))


# if __name__ == "__main__":
    # try:
    #     main(f_name)
    # except KeyboardInterrupt:
    #     # print("\n\033[1;31;0mTERMINATED BY USER\n")
    #     exit("TERMINATED BY USER")

