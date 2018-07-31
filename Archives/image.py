from PIL import Image
import time

color_map = []

# Load Image
im = Image.open('/home/aly/Downloads/d_66_I_94_B_16_Continuous_Core-1.png')
# im = Image.open('/home/aly/Desktop/bitmap.png')
# Convert to RGB
rgb_im = im.convert('RGB')
# Obtain image dimension for digitization
width, height = im.size
# Approximate Locations on Image for Lithological Identification
x_approx_litho = int((775./2550) * width) # on a 300dpi @ Pixel 775
y_start_approx_litho = int((793./21300) * height) # on a 300dpi @ Pixel 793
y_end_approx_litho = int((21178./21300) * height) # on a 300dpi @ Pixel 21178

# Obtain All Colors in the Lithological Identification
for j in range(y_start_approx_litho, y_end_approx_litho):
    r, g, b = rgb_im.getpixel((x_approx_litho, j))
    color_map.append(rgb_im.getpixel((x_approx_litho, j)))
    # print 775, j, r, g, b

print "No. of Original Colors %s" % color_map

color_map_unique = list(set(color_map))
print "No. of Unique Colors %s" % len(color_map_unique)


# for i in range(0, len(color_map) - 3, 4):
#     # print i
#     # time.sleep(5)
#     if color_map[i] != color_map[i + 3]:
#         if color_map[i] == (36, 31, 33):
#             color_map[i] = color_map[i + 3]
#             color_map[i + 1] = color_map[i + 3]
#             color_map[i + 2] = color_map[i + 3]
#             # color_map[i + 3] = color_map[i + 2]
#         elif color_map[i + 3] == (36, 31, 33):
#             color_map[i + 1] = color_map[i]
#             color_map[i + 2] = color_map[i]
#             color_map[i + 3] = color_map[i]
#         else:
#             color_map[i] = color_map[i + 3]
#             color_map[i + 1] = color_map[i + 3]
#             color_map[i + 2] = color_map[i + 3]

for i in range(0, len(color_map) - 1):
    if color_map[i] != color_map[i + 1]:
        if color_map[i + 1] == (36, 31, 33):
            color_map[i + 1] = color_map[i]
        else:
            color_map[i] = color_map[i + 1]

skipper = 10
for i in range(0, len(color_map) - skipper, (skipper + 1)):
    if color_map[i] != color_map[i + skipper]:
        if color_map[i] == (36, 31, 33):
            for j in range(0, skipper + 1):
                color_map[i + j] = color_map[i + 3]
            # color_map[i + 3] = color_map[i + 2]
        elif color_map[i + skipper] == (36, 31, 33):
            for j in range(0, skipper + 1):
                color_map[i + j] = color_map[i]
        else:
            for j in range(0, skipper + 1):
                color_map[i + j] = color_map[i]


ch_top = []
for i, j in enumerate(color_map):
    # print color_map[i + 1]
    # time.sleep(5)

    if i in range(15030, 17023):
        ch_top.append(round((1933. + (- 1078. + (793. + i)) / 95.), 2))
        if color_map[i] != color_map[i + 1]:
            # print round((1933. + (- 1078. + (793. + i)) / 95.), 2) , j
        # else:
            # print round((1933. + (- 1078. + (793. + i)) / 95.), 2), j
            ch = round((1933. + (- 1078. + (793. + i)) / 95.), 2)
            # print ch_top
            print "Depth Change at %s - %s Color %s" % (min(ch_top), ch, j)
            ch_top = []

# print "No. of Original Colors %s" % color_map
color_map_manipulate = list(set(color_map))
print "No. of Unique Colors %s" % len(color_map_manipulate)
