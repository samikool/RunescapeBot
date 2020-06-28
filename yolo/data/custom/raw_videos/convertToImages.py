# Program To Read video 
# and Extract Frames 
import cv2 
import argparse
import os
  
# Function to extract frames 
def FrameCapture(path, prefix): 
      
    # Path to video file 
    vidObj = cv2.VideoCapture(path) 
    
    # Used as counter variable 
    count = 0
  
    # checks whether frames were extracted 
    success = 1
  
    while success: 
  
        # vidObj object calls read 
        # function extract frames 
        success, image = vidObj.read() 

        # Saves the frames with frame-count
        if(success):
            cv2.imwrite(prefix+"frame%d.jpg" % count, image) 
        
        print("Converting frame: %d\r" %count, end="")
        count += 1

    print("Coverted ", count, " frames.")
    
# Driver Code 
if __name__ == '__main__': 
    parser = argparse.ArgumentParser()

    parser.add_argument('--v', type=str, required=True, help="Enter the path to the video file, relative to the script")
    parser.add_argument('--n', type=str, default='', help="This name will be the prefix to every fame in the form 'name_frameX.jpg'\n If left blank the default form will be 'frameX.jpg'")

    opt=parser.parse_args()

    vidPath = os.path.join(os.path.curdir, opt.v)
    
    #add underscore if needed
    prefix = opt.n
    if(prefix != ''):
        prefix += '_'

    # Calling the function 
    print("Coverting video at: ", vidPath)
    FrameCapture(vidPath, prefix) 
