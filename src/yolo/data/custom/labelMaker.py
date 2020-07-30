import os
import re
import json
import random
import shutil
from PIL import Image
from tqdm import tqdm

def loadLabelJSON():
    data = []

    with open('labelData.json') as file:
        data = json.load(file)

    return data

def parseJSONData(AllImageLabelData, classDict):
    returnData = {}

    for imageData in tqdm(AllImageLabelData):
        fileName = imageData['External ID']     #gets actual filename of image

        #load image demensions
        
        im = Image.open(os.path.join(os.curdir, 'named_images/'+fileName))
        imW,imH = im.size


        labeled = True if imageData['Label'] else False
        if labeled:
            objects = imageData['Label']['objects'] #array of objects in image

            fileString = '' #final string to write to text file 

            #for each object in image extract data and format it
            for objectData in objects:
                top = objectData['bbox']['top']
                left = objectData['bbox']['left']
                height = objectData['bbox']['height']
                width = objectData['bbox']['width']
                classs = objectData['value']

                #print(classs, top, left, width, height)

                #create bounding box from Labelbox.com data
                bbox = formatBoxData(classs, top, left, height, width, imW, imH)

                #print(bbox)

                fileString += createObjectString(bbox) + '\n'

            #print(fileString)
            returnData[fileName] = fileString
        else:
            print(fileName, " was not labeled...")

    return returnData

##function takes a bounding box and creates the textfile string 
def createObjectString(bbox):
    string = ''
    string  += str(bbox['class'])+' '+str(bbox['xcenter'])+' '+str(bbox['ycenter'])+' '+str(bbox['width'])+' '+str(bbox['height'])
    return string
    

## function formats bounding box from Labelbox.com into correct format
def formatBoxData(classs, top, left, height, width, imW, imH):
    classs = classDict[classs]

    #convert top and left to center coordinates
    xcenter = round( (left + width / 2) / imW, 5)
    ycenter = round( (top + height / 2) / imH, 5)

    #normalize height and width
    height = round(height/imH, 5)
    width = round(width/imW, 5)

    #print(classs, xcenter, ycenter, width, height)

    return {'class': classs, 'xcenter': xcenter, 'ycenter': ycenter, 'width': width, 'height': height}

def splitImageTextFileData(imageTextFileData):
    ttextFileData = {}
    vtextFileData = {}

    for k in imageTextFileData:
        r = random.uniform(0,1)
        if r <= 0.77:
            ttextFileData[k] = imageTextFileData[k]
        else:
            vtextFileData[k] = imageTextFileData[k]

    return ttextFileData,vtextFileData

def copyImages(src, dest, fileNames):
    for n in fileNames:
        f = os.path.join(src, n)
        s = shutil.copy(f,dest)

def writeImageLabelFile(imageTextFileData, labelDirectory):
    for fileName in tqdm(imageTextFileData):

        fileData = imageTextFileData[fileName]

        fileName = str(fileName)
        fileName = fileName.replace('.png', '.txt')
        
        filePath = os.path.join(labelDirectory, fileName)
        
        with open(filePath, 'w+') as file:
            file.write(fileData)
def writeDataFile(currentDirectory, classDict):
    filePath = os.path.join(currentDirectory, 'custom.data')

    numClasses = len(classDict)
    trainPath = os.path.join(currentDirectory, 'train.txt')
    validPath = os.path.join(currentDirectory, 'valid.txt')
    namePath = os.path.join(currentDirectory, 'custom.names')

    with open(filePath, 'w+') as file:
        file.write('classes='+str(numClasses)+'\n')
        file.write('train='+trainPath+'\n')
        file.write('valid='+validPath+'\n')
        file.write('names='+namePath)

def writeMasterTextFile(imageTextFileData, currentDirectory, imageDirectory, train):
    fileString = ''
    filePath = os.path.join(currentDirectory, 'train.txt') if train else os.path.join(currentDirectory, 'valid.txt')

    for file in imageTextFileData:
        imagePath = os.path.join(imageDirectory, file)
        fileString += imagePath + '\n'

    with open(filePath, 'w+') as file:
        file.write(fileString)



## function returns a dictionary of all the classes loaded from the names file
def loadLabels():
    classDict = {}
    with open('custom.names') as file:
        for i,line in enumerate(file.readlines()):
            line = line.strip('\n')
            classDict[line] = i
    return classDict

currentDirectory = os.path.abspath(os.path.curdir)
namedDirectory = os.path.join(currentDirectory, 'named_images')
imageDirectory = os.path.join(currentDirectory, 'images/train')
labelDirectory = os.path.join(currentDirectory, 'labels/train')
vimageDirectory = os.path.join(currentDirectory,'images/valid')
vlabelDirectory = os.path.join(currentDirectory, 'labels/valid')

print('Loading labels')
classDict = loadLabels()

print('Loading label data')
AllImageLabelData = loadLabelJSON()

print('Parsing data...')
imageTextFileData = parseJSONData(AllImageLabelData, classDict)

trainTextFileData,validTextFileData = splitImageTextFileData(imageTextFileData)

print('Copying images to correct paths...')
copyImages(namedDirectory, imageDirectory, list(trainTextFileData.keys()))
copyImages(namedDirectory, vimageDirectory, list(validTextFileData.keys()))

print('Writing label files...')
writeImageLabelFile(trainTextFileData, labelDirectory)
writeImageLabelFile(validTextFileData, vlabelDirectory)

print('Writing data file...')
writeDataFile(currentDirectory, classDict)

print('Writing master text file...')
writeMasterTextFile(trainTextFileData, currentDirectory, imageDirectory, True)
writeMasterTextFile(validTextFileData, currentDirectory, vimageDirectory, False)

print('Done.')