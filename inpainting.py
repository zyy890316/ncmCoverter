#!/usr/local/bin/python3
import numpy as np
from PIL import Image

def find_none_red(x,y,red_map):
    new_x = 0
    new_y = 0
    while (new_x < 5 or new_x > 1480) or (new_y < 5 or new_y > 1050):
        delt_x = np.random.randint(-30,30)
        delt_y = np.random.randint(-30,30)
        new_x = x + delt_x
        new_y = y + delt_y
    
    return (new_x,new_y)

def binarize_array(numpy_array, threshold=200):
    """Binarize a numpy array."""
    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                numpy_array[i][j] = 255
            else:
                numpy_array[i][j] = 0
    return numpy_array

# Open image and make RGB and HSV versions
im = Image.open("/Users/yiyiz/Downloads/AFWT10043691/nEO_IMG_AFWT10043691-05.jpg")

bw = im.convert('L')  # convert image to monochrome
bw = np.array(bw)
bw = binarize_array(bw, 300)
result=Image.fromarray(bw)
result.save('bw.jpg')

# Save Alpha if present, then remove
savedAlpha = None
if 'A' in im.getbands():
    savedAlpha = im.getchannel('A')
    im = im.convert('RGB')

# Make HSV version
HSVim = im.convert('HSV')

# Make numpy versions
RGBna = np.array(im)
HSVna = np.array(HSVim)

# Extract Hue
H = HSVna[:,:,0]

# Find all red pixels, i.e. where 340 < Hue < 20
lo,hi =  240,80
# Rescale to 0-255, rather than 0-360 because we are using uint8
lo = int((lo * 255) / 360)
hi = int((hi * 255) / 360)
red = np.where((H>lo) | (H<hi))

# Find all black pixels, i.e. where 340 < Hue < 20
lo,hi =  230,250
black = np.where((H>lo) | (H<hi))

# avg color
avg = np.mean(RGBna, axis=(0, 1))

# Make all red pixels red in original image
red_map = []
for i in range(0, red[0].size - 1):
    x = red[0][i]
    y = red[1][i]
    red_map.append((x,y))
for x,y in red_map:
    x_check,y_check = find_none_red(x,y,red_map)
    if (RGBna[(x,y)][0] > 100):
        RGBna[(x,y)] = RGBna[(x_check,y_check)]
        RGBna[(x,y)] = [255,0,0]
        
# Make all black pixels black in original image
black_map = []
for i in range(0, red[0].size - 1):
    x = black[0][i]
    y = black[1][i]
    black_map.append((x,y))
for x,y in black_map:
    x_check,y_check = find_none_red(x,y,red_map)
    if (RGBna[(x,y)][0] > 100):
        RGBna[(x,y)] = RGBna[(x_check,y_check)]
        RGBna[(x,y)] = [0,0,255]

count = red[0].size
print("Pixels matched: {}".format(count))

result=Image.fromarray(RGBna)

# Replace Alpha if originally present
if savedAlpha is not None:
    result.putalpha(savedAlpha)

result.save('result.jpg')