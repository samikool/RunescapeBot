import os
import re
import argparse
import json
import shutil

def rename(p):
    pat = re.compile('^'+p)

    with open('name_list.txt') as f:
        lines = f.readlines()
        
        for l in lines:
            r = re.search(pat,l)
            if r:
                print(l)

if __name__ == '__main__': 
    parser = argparse.ArgumentParser()
    parser.add_argument('--p', type=str, required=True, help="Enter the prefix you want to label the images with, this will probably be the name of object or target you train the image with")

    opt=parser.parse_args()
    p = opt.p

    