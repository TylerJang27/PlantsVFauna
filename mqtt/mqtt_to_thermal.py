from ast import parse
from gettext import find
from operator import index
import random
import shutil

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
            while lines[index].strip().find("t=767") == -1:
                index += 1
                new_image_buffer.append(lines[index].strip()[lines[index].strip().find("i:")+2:])
        image_buffer.append(new_image_buffer)
        index += 1
    f.close()


def copy_file():
    original = r'C:\Users\Frank\Desktop\ECE449\PlantsVFauna\output.txt'
    target = r'C:\Users\Frank\Desktop\ECE449\PlantsVFauna\copy.txt'
    shutil.copyfile(original, target)
    return target

if __name__ == "__main__":
    copy_file()
    read_file()
    print(image_buffer[0])
