'''
Created on Sep 23, 2019

@author: yiyiz
'''
import numpy as np
from PIL import Image

def binarize_array(numpy_array, threshold):
    """Binarize a numpy array."""
    new_array = np.copy(numpy_array)
    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                new_array[i][j] = 255
            else:
                new_array[i][j] = 0
    return new_array

# Open image and make RGB and HSV versions
im = Image.open("/Users/yiyiz/Downloads/AFWT10043691/nEO_IMG_AFWT10043691-06.jpg")

bw = im.convert('L')  # convert image to monochrome
bw = np.array(bw)
result=Image.fromarray(bw)
result.save('L.jpg')
for i in range(115, 160, 5):
    new_image = binarize_array(bw, i)
    result=Image.fromarray(new_image)
    result.save('threshold' + str(i) + '.jpg')