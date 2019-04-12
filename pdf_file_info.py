# /////////////////////////////////////////////////////////////// #
# !python2.7
# -*- coding: utf-8 -*-
# Python Script initially created on 03/03/19 
# Compiled by Aly @ Grasselli Geomechanics Group, UofT, 2019 
# Created using PyCharm 
# Current Version - Dated Apr 23, 2018
# /////////////////////////////////////////////////////////////// #

import time
# /// TIMER FUNCTION /// #

def calc_timer_values(end_time):
    minutes, sec = divmod(end_time, 60)
    if end_time < 60:
        return ("\033[1m%.2f seconds\033[0m" % end_time)
    else:
        return ("\033[1m%d minutes and %d seconds\033[0m." % (minutes, sec))


# /// ADMINISTRATIVE AND SORTING OF FILES IN FOLDER /// #


def red_text(val):  # RED Bold text
    tex = "\033[1;31m%s\033[0m" % val
    return tex


def green_text(val):  # GREEN Bold text
    tex = "\033[1;92m%s\033[0m" % val
    return tex


def bold_text(val):  # Bold text
    tex = "\033[1m%s\033[0m" % val
    return tex

def walk(obj, fnt, emb):
    '''
    If there is a key called 'BaseFont', that is a font that is used in the document.
    If there is a key called 'FontName' and another key in the same dictionary object
    that is called 'FontFilex' (where x is null, 2, or 3), then that fontname is
    embedded.

    We create and add to two sets, fnt = fonts used and emb = fonts embedded.
    '''
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

    return fnt, emb  # return the sets for each page

def main(f_name):
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument
    from PyPDF2 import PdfFileReader

    # for i in sub_dirs:

    fp = open(f_name, 'rb')
    parser = PDFParser(fp)
    # doc = PDFDocument(parser)
    pdf_toread = PdfFileReader(open(f_name, "rb"))
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
    print(
        green_text("PDF Engines %s %s, Made by %s on %s" % (str(Producer), str(Creator), str(Author), str(date)[2:10])))

    '''
    CHECK FONTS
    '''

    pdf = PdfFileReader(f_name)
    fonts = set()
    embedded = set()
    for page in pdf.pages:
        obj = page.getObject()
        f, e = walk(obj['/Resources'], fonts, embedded)
        fonts = fonts.union(f)
        embedded = embedded.union(e)

    # Check Font and return the possibility of OCR on the file.
    unembedded = fonts - embedded
    if fonts:
        print(green_text(('Font List => %s' % fonts,)))
        skip_file = 'no'
    else:
        print(red_text("No Fonts Found"))
        skip_file = "yes"
    if unembedded:
        print(red_text('\nUnembedded Fonts'))
        skip_file = "no"
    return skip_file

