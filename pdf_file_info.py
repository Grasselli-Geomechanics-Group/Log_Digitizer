###
# Script that loads the PDF and checks for compatibility.
###

import log_digitizer
def walk(obj, fnt, emb):
    """
    If there is a key called 'BaseFont', that is a font that is used in the document.
    If there is a key called 'FontName' and another key in the same dictionary object
    that is called 'FontFilex' (where x is null, 2, or 3), then that font name is embedded.

    We create and add to two sets, fnt =  and emb = fonts embedded.
    :param obj: object being passed, page in the PDF.
    :param fnt: fonts used
    :param emb: fonts embedded
    :return: return fnt,emb sets for each page
    :rtype: object
    """

    if not hasattr(obj, 'keys'):
        return None, None
    fontkeys = {'/FontFile', '/FontFile2', '/FontFile3'}  # set({'/FontFile', '/FontFile2', '/FontFile3'})
    if '/BaseFont' in obj:
        fnt.add(obj['/BaseFont'])
    if '/FontName' in obj:
        if [x for x in fontkeys if x in obj]:  # test to see if there is FontFile
            emb.add(obj['/FontName'])

    for k in obj.keys():
        walk(obj[k], fnt, emb)

    return fnt, emb  # return the sets for each page


def main(f_name):
    """
    Checks for the file compatibility in terms of fonts. It no fonts are embedded in the file, the script will not run on that file and all parts of the scripts (namely, the depth) is tied to the fact that it needs to read the values in the depth column.

    :param f_name: name of the PDF file to be processed
    :type f_name: string

    :return: True/False on whether the script can process the PDF.
    :rtype: bool
    """

    # Import and Read the PDF.
    from PyPDF2 import PdfFileReader

    pdf_toread = PdfFileReader(open(f_name, "rb"))

    # Read and assign variables based on the metadata
    pdf_info = pdf_toread.getDocumentInfo()
    try:
        date = pdf_info['/CreationDate']
        producer = pdf_info['/Producer']
        creator = pdf_info['/Creator']
        author = pdf_info['/Author']
    except KeyError:
        date = "Unknown"
        author = "Unknown"
        creator = "Unknown"
        producer = "Unknown"

    # print PDF metadata. Can be helpful if few files do not process when in batch mode. Maybe a pattern can be discovered.
    print(
        log_digitizer.green_text("PDF Engines %s %s, Made by %s on %s" % (str(producer), str(creator), str(author), str(date)[2:10])))

    # Read and assign font types.
    fonts = set()
    embedded = set()

    # Read all pages and gather font information.
    for page in pdf_toread.pages:
        obj = page.getObject()
        f, e = walk(obj['/Resources'], fonts, embedded)
        fonts = fonts.union(f)
        embedded = embedded.union(e)

    # Check Font and return the possibility of Text Extraction on the file.
    unembedded = fonts - embedded

    if fonts:  # Fonts found.
        print(log_digitizer.green_text('List of fonts found in PDF = %s' % fonts,))
        skip_file = False
    else:  # No Fonts found.
        print(log_digitizer.red_text("No Fonts Found"))
        skip_file = True

    if unembedded:  # Unrecognised embedded fonts found.
        print(log_digitizer.red_text('\nUnembedded/Unrecognised Fonts'))
        skip_file = False

    return skip_file

