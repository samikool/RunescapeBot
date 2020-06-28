import os
import re
import json
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
                classs = objectData['title']

                #print(classs, top, left, width, height)

                #create bounding box from Labelbox.com data
                bbox = formatBoxData(classs, top, left, height, width)

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
def formatBoxData(classs, top, left, height, width):
    classs = classDict[classs]

    #convert top and left to center coordinates
    xcenter = round( (left + width / 2) / 1920, 5)
    ycenter = round( (top + height / 2) / 1080, 5)

    #normalize height and width
    height = round(height/1080, 5)
    width = round(width/1920, 5)

    #print(classs, xcenter, ycenter, width, height)

    return {'class': classs, 'xcenter': xcenter, 'ycenter': ycenter, 'width': width, 'height': height}

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
    trainPath = os.path.join(currentDirectory, 'custom.txt')
    validPath = '' #os.path.join(currentDirectory,)
    validPath = trainPath
    namePath = os.path.join(currentDirectory, 'custom.names')

    with open(filePath, 'w+') as file:
        file.write('classes='+str(numClasses)+'\n')
        file.write('train='+trainPath+'\n')
        file.write('valid='+validPath+'\n')
        file.write('names='+namePath)

def writeMasterTextFile(imageTextFileData, currentDirectory, imageDirectory):
    fileString = ''
    filePath = os.path.join(currentDirectory, 'custom.txt')

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
imageDirectory = os.path.join(currentDirectory, 'images')
labelDirectory = os.path.join(currentDirectory, 'labels')


print('Loading labels')
classDict = loadLabels()

print('Loading label data')
AllImageLabelData = loadLabelJSON()

print('Parsing data...')
imageTextFileData = parseJSONData(AllImageLabelData, classDict)

print('Writing label files...')
writeImageLabelFile(imageTextFileData, labelDirectory)

print('Writing data file...')
writeDataFile(currentDirectory, classDict)

print('Writing master text file...')
writeMasterTextFile(imageTextFileData, currentDirectory, imageDirectory)

print('Done.')