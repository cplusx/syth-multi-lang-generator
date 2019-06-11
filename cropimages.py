import h5py as h5
import numpy as np
# import matplotlib.pyplot as plt
import cv2
import math
from PIL import Image
import sys
import json
import os

def calculateDistance(p1,p2):
    dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    return dist

def extendBox(pts1,pts2):
    p1slope = (pts1[1][1]-pts1[0][1])/(pts1[1][0]-pts1[0][0])
    p2slope = (pts2[1][1]-pts2[0][1])/(pts2[1][0]-pts2[0][0])
    height1 = calculateDistance(pts1[0],pts1[3])
    height2 = calculateDistance(pts2[0],pts2[3])

    if(height1 > height2):
        xdif = pts2[0][0] - pts1[0][0]
        if xdif > 0:
            extendx = pts2[1][0] - pts1[1][0]
            newpts = pts1
            totalslope=(pts2[1][1]-pts1[0][1])/(pts2[1][0]-pts1[0][0])
            newpts[1][0] = pts1[1][0] + extendx
            newpts[1][1] = pts1[1][1] + extendx*totalslope
            newpts[2][0] = pts1[2][0] + extendx
            newpts[2][1] = pts1[2][1] + extendx*totalslope
        else:
            extendx = pts1[1][0] - pts2[1][0]        
            newpts = pts1
            totalslope=(pts1[1][1]-pts2[0][1])/(pts1[1][0]-pts2[0][0])
            newpts[1][0] = pts1[1][0] - extendx
            newpts[1][1] = pts1[1][1] - extendx*totalslope
            newpts[2][0] = pts1[2][0] - extendx
            newpts[2][1] = pts1[2][1] - extendx*totalslope
    else:
        xdif = pts2[0][0] - pts1[0][0]
        if xdif > 0:
            extendx = pts2[0][0] - pts1[0][0]
            newpts = pts2
            totalslope=(pts2[1][1]-pts1[0][1])/(pts2[1][0]-pts1[0][0])
            newpts[0][0] = pts2[0][0] - extendx
            newpts[0][1] = pts2[0][1] - extendx*totalslope
            newpts[3][0] = pts2[3][0] - extendx
            newpts[3][1] = pts2[3][1] - extendx*totalslope
        else:
            extendx = pts1[0][0] - pts2[0][0]
            newpts = pts2
            totalslope=(pts1[1][1]-pts2[0][1])/(pts1[1][0]-pts2[0][0])
            newpts[0][0] = pts2[0][0] + extendx
            newpts[0][1] = pts2[0][1] + extendx*totalslope
            newpts[3][0] = pts2[3][0] + extendx
            newpts[3][1] = pts2[3][1] + extendx*totalslope
    return newpts

def flipIfInverted(pts):
     if(pts[0][1] < pts[3][1]):
          return pts
     else:
          newpoints = []
          newpoints.append(pts[3])
          newpoints.append(pts[2])
          newpoints.append(pts[1])
          newpoints.append(pts[0])
          newpointsarray = np.array(newpoints)
          return newpointsarray


def fixRotatedPoints(pts):
     if(pts[0][0] <= pts[1][0]):
          min_x=pts[0][0]
          min_x_index=0
          second_min_x=pts[1][0]
          second_min_x_index=1
     else:
          min_x=pts[1][0]
          min_x_index=1
          second_min_x=pts[0][0]
          second_min_x_index=0
     for i in range(2,4):
          if(pts[i][0] < min_x):
               second_min_x=min_x
               second_min_x_index=min_x_index
               min_x=pts[i][0]
               min_x_index=i
          elif(pts[i][0] < second_min_x):
               second_min_x=pts[i][0]
               second_min_x_index=i
     print(min_x_index)
     print(min_x)
     print(second_min_x_index)
     print(second_min_x)
     if(pts[min_x_index][1] < pts[second_min_x_index][1]):
          start_index=min_x_index
     else:
          start_index=second_min_x_index
     newpoints = []
     for i in range(start_index, start_index + 4):
          if(i < 4):
               newpoints.append(pts[i])
          else:
               newpoints.append(pts[i-4])
     newpointsarray = np.array(newpoints)
     print("Top left was index: " + str(start_index))
     return newpointsarray


def get_line_bb_matrix(dname, imgdata, wordbb, origlabels):            
    imgdata = cv2.cvtColor(imgdata, cv2.COLOR_BGR2RGB)
    imgname = dname
    # wordbb = f['data'][filename].attrs['wordBB']
    # origlabels = f['data'][filename].attrs['txt']

    numwords = []
    labels = []
    for label in enumerate(origlabels):
        for l in label[1].splitlines():
            labels.append(l.strip())
    for words in enumerate(labels):
        numwords.append(len(words[1].split()))
    bb_list = wordbb
    text_im = imgdata

    bbs = wordbb
    ni = bbs.shape[0]
    bbcount = 0


    master_matrix = np.ones(shape=(2, 4, len(labels)), dtype=float)
    count_lb = 0
    for labelcount in range(len(labels)):
        if(numwords[labelcount] ==1):
            bb = bbs[:,:,bbcount]
            p0 = [bb[0][0],bb[1][0]]
            p1 = [bb[0][1],bb[1][1]]
            p2 = [bb[0][2],bb[1][2]]
            p3 = [bb[0][3],bb[1][3]]
            points =  np.array([p0,p1,p2,p3], dtype=float)

            bbcount += 1
        else:
            points = []
            for j in range(numwords[labelcount]):
                bb = bbs[:,:,bbcount+j]
                p0 = [bb[0][0],bb[1][0]]
                p1 = [bb[0][1],bb[1][1]]
                p2 = [bb[0][2],bb[1][2]]
                p3 = [bb[0][3],bb[1][3]]
                points = np.array([p0,p1,p2,p3])
                pts = np.array([p0,p1,p2,p3],np.float)
                pts = pts.reshape((-1,1,2))

                if(j>0):
                    curpoints =  extendBox(curpoints,points)
                elif(j==0):
                    curpoints = points
                points = curpoints
            
            bbcount += numwords[labelcount]
        

        intpoints =  np.array(points,np.float)
        intpoints = flipIfInverted(intpoints)
        
        p0x=intpoints[0][0]
        p0y=intpoints[0][1]
        p1x=intpoints[1][0]
        p1y=intpoints[1][1]
        p2x=intpoints[2][0]
        p2y=intpoints[2][1]
        p3x=intpoints[3][0]
        p3y=intpoints[3][1]

        intpoints = intpoints.reshape((-1,1,2))
        
        master_matrix[0, :, count_lb] = intpoints[:, 0, 0]
        master_matrix[1, :, count_lb] = intpoints[:, 0, 1] 

        count_lb +=1
    
    # print("master_matrix.shape = ",master_matrix)

    return master_matrix,labels
