import numpy as np
import re
import cv2
import matplotlib.pyplot as plt

# Your image
raw_values = np.array([[]])

# Enter the image height and width
height = int(len(raw_values))
width  = int(len(raw_values[0]))

def get_color(j):
    i = int(j)
    R_color = 0
    G_color = 0
    B_color = 0
    if i >= 0 and i < 30:
        R_color = 0
        G_color = 0
        B_color = 20 + (120.0 / 30.0) * i
    if i >= 30 and i < 60:
        R_color = (120.0 / 30) * (i - 30.0)
        G_color = 0
        B_color = 140 - (60.0 / 30.0) * (i - 30.0)
    if i >= 60 and i < 90:
        R_color = 120 + (135.0 / 30.0) * (i - 60.0)
        G_color = 0
        B_color = 80 - (70.0 / 30.0) * (i - 60.0)
    if i >= 90 and i < 120:
        R_color = 255
        G_color = 0 + (60.0 / 30.0) * (i - 90.0)
        B_color = 10 - (10.0 / 30.0) * (i - 90.0)
    if i >= 120 and i < 150:
        R_color = 255
        G_color = 60 + (175.0 / 30.0) * (i - 120.0)
        B_color = 0
    if i >= 150 and i <= 180:
        R_color = 255
        G_color = 235 + (20.0 / 30.0) * (i - 150.0)
        B_color = 0 + 255.0 / 30.0 * (i - 150.0)
    return R_color, G_color, B_color

# Create numpy array of BGR triplets
im = np.zeros((height,width,3), dtype=np.uint8)
a = raw_values.astype(np.int)
for row in range (height):
    for col in range(width):
        value = 180*(int(raw_values[row][col]) - int(np.amin(a))) / (int(np.amax(a))-int(np.amin(a)))
        R, G, B = get_color(value)
        im[row,col] = (B,G,R)

print(im)

# Save to disk
cv2.imwrite('image.png', im)
