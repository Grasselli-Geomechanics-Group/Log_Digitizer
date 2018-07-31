#!/usr/bin/python
#

from PyPDF2 import PdfFileWriter, PdfFileReader


with open("/home/aly/Desktop/Progress_Logs/d_66_I_94_B_16_Continuous_Core.pdf", "rb") as in_f:
    log_input = PdfFileReader(in_f)
    numPages = log_input.getNumPages()
    x1, y1, x2, y2 = log_input.getPage(0).mediaBox
    print("Document has %s page(s) of dimensions %s X %s." % (numPages, int(x2 - x1), int(y2 - y1)))

    # Crop off the lithology column
    litho_log_output = PdfFileWriter()
    for i in range(numPages):
        litho_log = log_input.getPage(i)
        litho_log.mediaBox.lowerLeft = (185, y2)
        litho_log.mediaBox.upperRight = (125, y1)
        litho_log_output.addPage(litho_log)

    with open("/home/aly/Desktop/Progress_Logs/litho_log.pdf", "wb") as out_f:
        litho_log_output.write(out_f)
    out_f.close()

    # # Crop off the sedimentary column
    sed_struc_log_output = PdfFileWriter()
    for i in range(numPages):
        sed_struc_log = log_input.getPage(i)
        sed_struc_log.mediaBox.lowerLeft = (240, y2)
        sed_struc_log.mediaBox.upperRight = (190, y1)
        sed_struc_log_output.addPage(sed_struc_log)

    with open("/home/aly/Desktop/Progress_Logs/sed_struc_log.pdf", "wb") as out_f:
        litho_log_output.write(out_f)
    out_f.close()

    # Crop off the environment column
    env_log_ouput = PdfFileWriter()
    for i in range(numPages):
        env_log = log_input.getPage(i)
        env_log.mediaBox.lowerLeft = (575, y2)
        env_log.mediaBox.upperRight = (522, y1)
        env_log_ouput.addPage(env_log)

    with open("/home/aly/Desktop/Progress_Logs/env_log.pdf", "wb") as out_f:
        env_log_ouput.write(out_f)
    out_f.close()

    # Crop off the surfaces column
    surface_log_ouput = PdfFileWriter()
    for i in range(numPages):
        surface_log = log_input.getPage(i)
        surface_log.mediaBox.lowerLeft = (375, y2)
        surface_log.mediaBox.upperRight = (350, y1)
        surface_log_ouput.addPage(surface_log)

    with open("/home/aly/Desktop/Progress_Logs/surface_log.pdf", "wb") as out_f:
        surface_log_ouput.write(out_f)
    out_f.close()

in_f.close()

pdf_name_1 = ["/home/aly/Desktop/Progress_Logs/litho_log.pdf", "/home/aly/Desktop/Progress_Logs/sed_struc_log.pdf", "/home/aly/Desktop/Progress_Logs/env_log.pdf", "/home/aly/Desktop/Progress_Logs/surface_log.pdf"]

from wand.image import Image
from wand.color import Color
for pdf_name in pdf_name_1:
    with Image(filename=pdf_name, resolution=600) as img:
        with Image(width=img.width, height=img.height, background=Color("white")) as bg:
            bg.composite(img, 0, 0)
            bg.save(filename=os.path.splitext(pdf_name)[0] + '_python_convert.png')

#
# global rgb_im, width, height
# Image.MAX_IMAGE_PIXELS = None
# # Load Image
# im = Image.open(file_name)
# # Convert to RGB
# rgb_im = im.convert('RGB')
# # Obtain image dimension for digitization
# width, height = im.size
# print("Image Loaded")
# # print(width, height)
# return rgb_im, width, height