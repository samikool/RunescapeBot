# RunescapeBot
This python project is essentially a botting master/client for OSRS. It uses Yolov3 object detection along with more primitive methods to automate repetitive tasks in Runescape. The end goal of this code base will be to provide a master that can control many intances of a botclient. The botclient will then handle all of its own controlling and decision making when it comes to executing tasks. 

## Tech
Right now most of the project is written in Python. It makes developement pretty easy, and since it is controlling a simple game like runescape, performance has not been an issue. Right now it is running on Arch Linux. It uses Xvfb to create virtual displays which the clients run in. Pyautogui is used to control the keyboard and mouse seperately for each client. 

## Image Detection
The bot makes use of Yolov3 image detection. It can recognize different types of trees, and other objects. The sky is the limit here and it could potentially be trained to recognize anything provided there are enough pictures. Pictures are gathered by taking short recordings and using python to split the video into a picture for every frame. The data is then quadroupled by fliping it horizontally, vertically, and both vertically and horizontally. 

## Current Status
As of now this project is in it's infancy. Although a lot of initial tech hurdles have been overcome, there is still a lot of work that needs to be done, before I would consider it stable. 
