from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
import time
import numpy as np
from scipy import spatial
from collections import OrderedDict

locations = {'Name:' : [475, 734], 'Well Location:' : [100, 748] , 'Fm/Strat. Unit:' : [308, 734], 'Date:' : [469, 706]}

'''
CONVERT BYTES TO STRING
'''

# Convert the given unicode string to a bytestring, using the standard encoding, unless it's already a bytestring.

def to_bytestring (s, enc='utf-8'):
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)

# SCRIPT OBTAINED FROM https://stackoverflow.com/questions/22898145/how-to-extract-text-and-text-coordinates-from-a-pdf-file
# Open a PDF file.
fp = open('/home/aly/Desktop/Talisman_c-65-F_Page 1.pdf', 'rb')

# Create a PDF parser object associated with the file object.
parser = PDFParser(fp)

# Create a PDF document object that stores the document structure.
# Password for initialization as 2nd parameter
document = PDFDocument(parser)

# Check if the document allows text extraction. If not, abort.
if not document.is_extractable:
    raise PDFTextExtractionNotAllowed

# Create a PDF resource manager object that stores shared resources.
rsrcmgr = PDFResourceManager()

# Create a PDF device object.
device = PDFDevice(rsrcmgr)

# BEGIN LAYOUT ANALYSIS
# Set parameters for analysis.
laparams = LAParams()

# Create a PDF page aggregator object.
device = PDFPageAggregator(rsrcmgr, laparams=laparams)

# Create a PDF interpreter object.
interpreter = PDFPageInterpreter(rsrcmgr, device)


def update_page_text_hash (h, lt_obj, pct=0.2):
    """Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""
    x0 = lt_obj.bbox[1]
    x1 = lt_obj.bbox[3]
    key_found = False
    for k, v in h.items():
        hash_x0 = k[1]
        if x0 >= (hash_x0 * (1.0-pct)) and (hash_x0 * (1.0+pct)) >= x0:
            hash_x1 = k[0]
            if x1 >= (hash_x1 * (1.0-pct)) and (hash_x1 * (1.0+pct)) >= x1:
                # the text inside this LT* object was positioned at the same
                # width as a prior series of text, so it belongs together
                key_found = True
                v.append(to_bytestring(lt_obj.get_text()))
                h[k] = v
    if not key_found:
        # the text, based on width, is a new series,
        # so it gets its own series (entry in the hash)
        h[(x0,x1)] = [to_bytestring(lt_obj.get_text())]
    return h

def parse_obj(lt_objs, y_loc=700):
    coord, corel = [], {}
    depths = {}
    # loop over the object list
    for obj in lt_objs:

        # bbox(bounding box) attribute, which is a four - part  tuple of the object's page position: (x0, y0, x1, y1)

        # if it's a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            print("%6d, %6d, %6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3], obj.get_text().replace('\n', '_')))
            coord.append([obj.bbox[0], obj.bbox[1]])
            corel[obj.get_text().replace('\n', '')] = [obj.bbox[0], obj.bbox[1]]

        # if it's a container, recurse. That is, LTFigure objects are containers for other LT* objects, so recurse through the children
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs)

    coord_myarray = np.asarray(coord)
    for k, v in locations.items():
        alpha = coord_myarray[spatial.KDTree(coord_myarray).query(v)[1]] # Lookup nearest point to predefined location
        for k1, v1 in corel.items():
            if v1 == list(alpha):
                print(k, '\t', k1)

    for obj in lt_objs:
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            if int(obj.bbox[0]) in range(40,60) and int(obj.bbox[1]) < y_loc:
                try:
                    depths[int(obj.bbox[1])] = int(obj.get_text().replace('\n', ''))
                except ValueError:
                    print("Error in Depth Column")
                    # for y in range(10, 100, 10):
                    #     parse_obj(lt_objs, y_loc-y)
                    exit("Status 10 - Text identified in the Depth Column. Please change value of y_loc.")


    # Sort by location in the column
    depths = OrderedDict(sorted(depths.items(), key=lambda t: t[0]))
    a, b = [], []
    for key in depths:
        print("%s: %s" % (key, depths[key]))
        a.append(depths[key])
        b.append(key)


    check_depth_column('Depths Values', a)
    check_depth_column('Pixel Location', b)

    print(a, b)
    ratio = abs((a[0] - a[-1]) / (b[0] - b[-1]))
    print("Ratio : %s" % ratio)


    for obj in lt_objs:
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            if int(obj.bbox[0]) in range(524, 535) and int(obj.bbox[1]) < y_loc:
                print(obj.bbox[1], obj.bbox[1] / ratio, obj.get_text().replace('\n', '_'))

def check_depth_column(name, list_values):
    if name == 'Depth Values':
        # list_values = list(reversed(list_values))
        for x, i in enumerate(list_values):
            if x < len(list_values) - 1 :
                    if list_values[x] < list_values[x + 1]:
                        print("Check the depth column for Typos")
                        exit(11)
    unique_values = len(set(np.diff(list_values)))
    diff = abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values))))
    if len(set(np.diff(list_values))) == 1:
         print("%s in the DEPTH COLUMN CHECKED" % name)
    elif abs(max(set(np.diff(list_values))) - min(set(np.diff(list_values)))) < 2:
        print("MINOR Error in scale of %s, off by %s units" % (name, diff))
    else:
        exit("Status 12 - MINOR Error in scale of %s, off by %s units\nValues are %s" % (name, diff, np.diff(list_values)))

# loop over all pages in the document
for page in PDFPage.create_pages(document):

    # read the media box that is the page size as list of 4 integers x0 y0 x1 y1
    print(page.mediabox)

    # read the page into a layout object
    # receive the LTPage object for this page
    interpreter.process_page(page)
    layout = device.get_result()
    # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.

    # extract text from this object
    parse_obj(layout._objs)