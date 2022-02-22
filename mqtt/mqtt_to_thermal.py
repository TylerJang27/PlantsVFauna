from ast import parse
from gettext import find
from operator import index
import random
import shutil
import numpy as np
import re
import cv2
import matplotlib.pyplot as plt

image_buffer = []

def create_test_communication():
    comm_list = []
    for i in range(768):
        comm_list.append("t=" + str(i) + " i:" + str(random.randint(0,255)))
    return comm_list    

def parse_comms(comm_list):
    index_list = []
    for i in comm_list:
        start = i.find(":")
        index_list.append(i[start + 1:])
    return index_list 

def read_file():
    f = open("copy.txt", "r")
    lines = f.readlines()
    index = 0
    while index < len(lines):
        if lines[index].strip().find("t=0") != -1:
            new_image_buffer = []
            new_image_buffer.append(int(lines[index].strip()[lines[index].strip().find("i:") + 2:]))
            while lines[index].strip().find("t=767") == -1:
                index += 1
                new_image_buffer.append(int(lines[index].strip()[lines[index].strip().find("i:") + 2:]))
        image_buffer.append(new_image_buffer)
        index += 1
    f.close()


def copy_file():
    original = r'C:\Users\Frank\Desktop\ECE449\PlantsVFauna\mqtt\output.txt'
    target = r'C:\Users\Frank\Desktop\ECE449\PlantsVFauna\mqtt\copy.txt'
    shutil.copyfile(original, target)
    return target

def make_image(raw_values, index):
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
    # Save to disk
    string = "image" + str(index) + ".png"
    cv2.imwrite(string, im)

def make_numpy_array(image_list):
    image_array = np.array(image_list)
    np_image = np.reshape(image_array, (24, 32))
    print(np_image)
    return np_image

if __name__ == "__main__":
    copy_file()
    read_file()
    for index in range(len(image_buffer)):
        raw_values = make_numpy_array(image_buffer[index])
        make_image(raw_values, index)
