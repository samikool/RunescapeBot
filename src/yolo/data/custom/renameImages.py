import os
import re
import json
from tqdm import tqdm

def renamePictures(currentDirectory, imageDirectory, labelDirectory):
    imageList = os.listdir(imageDirectory)
    imageList.sort()
    pattern = re.compile("^image")

    correctImageCount = 0
    renameImages = []

    #find images that are already named
    for i,file in enumerate(imageList):
        if(pattern.search(file)):
            correctImageCount += 1
        else:
            renameImages.append(file)

    print(correctImageCount, 'images correctly named.')
    print(len(imageList) - correctImageCount, 'images will be renamed.')

    #rename images 
    if(len(imageList) - correctImageCount != 0):
        for i,file in tqdm(enumerate(renameImages)):
            imageNum = correctImageCount+i

            oldPath = os.path.join(imageDirectory, file)
            newPath = os.path.join(imageDirectory, 'image'+f"{imageNum:010d}"+".png")

            os.rename(oldPath, newPath)

            tqdm.write(str(file)+' -> image'+f"{imageNum:010d}"+".png\r", end="")

currentDirectory = os.path.abspath(os.path.curdir)
imageDirectory = os.path.join(currentDirectory, 'images')
labelDirectory = os.path.join(currentDirectory, 'labels')

print('Renaming images...')
renamePictures(currentDirectory, imageDirectory, labelDirectory)