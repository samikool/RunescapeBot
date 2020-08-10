import os
import re
import random
import shutil

from tqdm import tqdm

def getImgDict(imgDir):
    l = os.listdir(imgDir)
    d = dict()
    for file in l:
        if file == 'classes.txt':
            continue

        img = True if file.endswith('.png') else False
        name = file[:-4]

        if not d.get(name):
            d[name] = dict()

        if(img):
            d[name]['img'] = file
        else:
            d[name]['lbl'] = file

    return d


#driver code
if __name__ == '__main__':
    imgDir = os.path.join(os.curdir, 'named_images/labeled')
    
    imgTDir = os.path.join(os.curdir, 'images/train')
    imgVDir = os.path.join(os.curdir, 'images/valid')

    lblTDir = os.path.join(os.curdir, 'labels/train')
    lblVDir = os.path.join(os.curdir, 'labels/valid')

    d = getImgDict(imgDir)

    trainTxtS = ''
    validTxtS = ''

    tc = 0
    vc = 0
    for f in tqdm(d):
        img = d[f]['img']
        lbl = d[f]['lbl']

        imgP = os.path.join(imgDir, img)
        lblP = os.path.join(imgDir, lbl)

        train = True if random.random() < 0.8 else False 

        #image is part of training data
        if train:
            shutil.copy(imgP,imgTDir)
            shutil.copy(lblP,lblTDir)
            trainTxtS += os.path.join(imgTDir,img)+'\n'
            tc += 1

        #image is part of valid data
        else:
            shutil.copy(imgP,imgVDir)
            shutil.copy(lblP,lblVDir)
            validTxtS += os.path.join(imgVDir,img)+'\n'
            vc += 1

    with open('train.txt', 'w') as t, open('valid.txt', 'w') as v:
        t.write(trainTxtS)
        v.write(validTxtS)

    print('Finished with: Train:',tc,'Valid:',vc,'Split:',tc/(tc+vc))