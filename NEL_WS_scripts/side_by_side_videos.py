#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 13:54:31 2019

@author: nel-lab

MODIFIED BY WILLIAM ON NOV 8 2019
- added png to avi conversion
- added some directory organization 
"""
#%%
import numpy as np
import os 
import cv2

path = '/Applications/NoniCloud Desktop/GiovannucciLab/pointer_cal_images/' 
os.chdir(path)
rootDirectory = path

# Read the video from specified path 
cam1 = cv2.VideoCapture('/Applications/NoniCloud Desktop/GiovannucciLab/pointer_cal_images/Neurospark_side.mp4') 
cam2 = cv2.VideoCapture('/Applications/NoniCloud Desktop/GiovannucciLab/pointer_cal_images/Neurospark_front.mp4') 
cam3 = cv2.VideoCapture('/Applications/NoniCloud Desktop/GiovannucciLab/pointer_cal_images/Neurospark_bottom.mp4') 
cam4 = cv2.VideoCapture('')
cam5 = cv2.VideoCapture('')

#%%
try: 
      
    # creating a folder named data 
    if not os.path.exists('data'): 
        os.makedirs('data') 
  
# if not created then raise error 
except OSError: 
    print ('Error: Creating directory of data') 
  
currentframe = 0

while(True): 
      
    # reading from frame 
    ret1,frame1 = cam1.read() 
    ret2,frame2 = cam2.read() 
    ret3,frame3 = cam3.read() 
    ret4,frame4 = cam4.read() 
    ret5,frame5 = cam5.read() 
    
    
    x = frame1.shape[0]
    y = frame1.shape[1]
    
    frame = np.zeros(((x,5*y,3)))
    frame[0:x,0:y] = frame4[:,:]
    frame[0:x,y:2*y] = frame1[:,:]
    frame[0:x,2*y:3*y] = frame3[:,:]
    frame[0:x,3*y:4*y] = frame2[:,:]
    frame[0:x,4*y:5*y] = frame5[:,:]
    
  
    if ret1: 
        # if video is still left continue creating images 
        name = './data/frame' + str(currentframe).zfill(5) + '.jpg'
        print ('Creating...' + name) 
  
        # writing the extracted images 
        cv2.imwrite(name, frame) 
  
        # increasing counter so that it will 
        # show how many frames are created 
        currentframe += 1
    else: 
        break
  
# Release all space and windows once done 
cam1.release() 
cam2.release() 
cam3.release() 
cam4.release() 
cam5.release() 
cv2.destroyAllWindows() 

import cv2
import shutil

imageDirectory = rootDirectory + '/data'
image_folder = imageDirectory
os.chdir(imageDirectory)
video_name2 =  'Neurospark_conc_20FPS.avi'

#numFiles = len([img for img in os.listdir(image_folder) if img.endswith(".png")])
images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
images.sort()
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

video = cv2.VideoWriter(video_name2, 0, 20, (width, height))

for image in images:
    video.write(cv2.imread(os.path.join(image_folder, image)))

shutil.move(video_name2, rootDirectory)
   
video.release()


#%%
#    import pdb
#    pdb.set_trace()