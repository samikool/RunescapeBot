#Train
#Don't forget to edit the network if you are training for more clasess last edit: filters=27 classes=4 -> filters=30 classes=5
python3 train.py --epochs 1000 --batch-size 1 --cfg cfg/yolov3-spp.cfg --data data/custom/custom.data

#Test 
python3 detect.py --cfg cfg/yolov3-spp.cfg --names data/custom/custom.names --weights weights/last.pt --source data/custom/test_images 

#Create Display
rm -rf /var/tmp/$i
mkdir /var/tmp/$i
Xvfb :$i -screen 0 1920x1080x24+32 -fbdir /var/tmp/$i &
export DISPLAY=:$i
exec startlxde &

#Start VNC Server to see Display
exec x11vnc -geometry 1920x1080 -display :$display -ncache 10 -N -noipv6 -shared -nopw -onetile &

#Possibly get open display
xdpyinfo -display :1 | grep unable 

#record screen 1.0 -> display 1 2.0 -> display 2 etc.
ffmpeg -f x11grab -video_size 1280x720 -framerate 60 -i :1.0 -c:v h264_nvenc -q:v 0 /git/runescapebot/test.mkv

ffmpeg -f x11grab -video_size 1280x720 -framerate 60 -i :2.0 -c:v h264_nvenc -q:v 0 /git/runescapebot/test_2.mp4
ffmpeg -f x11grab -video_size 1280x720 -framerate 60 -i :3.0 -c:v h264_nvenc -q:v 0 /git/runescapebot/test_3.mp4
ffmpeg -f x11grab -video_size 1280x720 -framerate 60 -i :4.0 -c:v h264_nvenc -q:v 0 /git/runescapebot/test_4.mp4
ffmpeg -f x11grab -video_size 1280x720 -framerate 60 -i :5.0 -c:v h264_nvenc -q:v 0 /git/runescapebot/test_5.mp4