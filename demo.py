#!/usr/bin/env python

# --------------------------------------------------------
# Faster R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""

import _init_paths
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import caffe, os, sys, cv2
import argparse
import time

CLASSES = ('__background__','car')

NETS = {'vgg16': ('VGG16',
                  'VGG16_faster_rcnn_final.caffemodel'),
        'zf': ('ZF',
                  'ZF_faster_rcnn_final.caffemodel'),
        'vgg1024': ('VGG_CNN_M_1024',
                    'VGG_CNN_M_1024_faster_rcnn_final.caffemodel')}

flag = 1
num_car = 0

def vis_detections_video(im, class_name, dets, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    #print car Number
    print(len(inds))
    word = 'number of cars: ' + str(len(inds))
    global num_car
    num_car = len(inds)
    cv2.putText(im,word,(980,680),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1.0,(120,255,100),2)

    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]
        cv2.rectangle(im,(bbox[0],bbox[1]),(bbox[2],bbox[3]),(50,50,255),2)
        #cv2.rectangle(im,(int(bbox[0]),int(bbox[1])-10),(int(bbox[0]+200),int(bbox[1])+10),(10,10,10),-1)
        #cv2.putText(im,'{:s} {:.3f}'.format(class_name, score),(int(bbox[0]),int(bbox[1]-2)),cv2.FONT_HERSHEY_SIMPLEX,.45,(255,255,255))#,cv2.CV_AA)
    return im

def demo_video(net,im):
    """Detect object classes in an image using pre-computed object proposals."""

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(net, im)
    timer.toc()
    print ('Detection took {:.3f}s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    # Visualize detections for each class
    CONF_THRESH = 0.8
    NMS_THRESH = 0.3

    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]

        vis_detections_video(im, cls, dets, thresh=CONF_THRESH)

    cv2.imwrite(os.path.join('output',str(time.time())+'.jpg'),im)
    cv2.imshow('ret',im)

    # if timer.total_time <= 0.1:
    #     time_wait = 99 - 1000*timer.total_time
    #     print('waittime='+ str(time_wait))
    #     cv2.waitKey(int(time_wait))
    # else:
    #     pass

    # cv2.imwrite('/home/wwh/Desktop/3.jpg',im)
    write_picture_file(im)

    file = open('/home/wwh/Desktop/number.txt','w')
    file.write(str(num_car))
    file.close()

    #cv2.waitKey(1)

def tracking(frame,bbox):
    # cv2.imshow('ret',frame)
    # cv2.waitKey(1)
    timer = cv2.getTickCount()
    cv2.waitKey(10)
    # Update tracker
    ok, bbox = tracker.update(frame)

    # Calculate Frames per second (FPS)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
    # Draw bounding box

    # Tracking success
    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
    # Display tracker type on frame
    cv2.putText(frame, 'KCF' + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
    # Display FPS on frame
    cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
    # Display result
    write_picture_file(frame)
    return bbox


def write_picture_file(frame):
    global flag
    if flag == 0:
        os.rename('/home/wwh/Desktop/1.jpg','/home/wwh/Desktop/0.jpg')
        cv2.imwrite('/home/wwh/Desktop/1.jpg',frame)
        flag = 1

    if flag == 1:
        os.rename('/home/wwh/Desktop/3.jpg','/home/wwh/Desktop/2.jpg')
        cv2.imwrite('/home/wwh/Desktop/3.jpg',frame)
        flag = 0
    else:
        pass

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Faster R-CNN demo')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
                        choices=NETS.keys(), default='vgg1024')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals

    args = parse_args()

    prototxt = os.path.join(cfg.MODELS_DIR, NETS[args.demo_net][0],
                            'faster_rcnn_alt_opt', 'faster_rcnn_test.pt')       #revise
    caffemodel = os.path.join(cfg.DATA_DIR, 'faster_rcnn_models',
                              NETS[args.demo_net][1])

    if not os.path.isfile(caffemodel):
        raise IOError(('{:s} not found.\nDid you run ./data/script/'
                       'fetch_faster_rcnn_models.sh?').format(caffemodel))

    if args.cpu_mode:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(args.gpu_id)
        cfg.GPU_ID = args.gpu_id
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)

    print '\n\nLoaded network {:s}'.format(caffemodel)

    #init tracking
    tracker = cv2.TrackerKCF_create()
    bbox = 1
    #get video from webcam and set size
    cap = cv2.VideoCapture(0)
    cap.set(3,1280)
    cap.set(4,720)

    while True:
        ret, image = cap.read()

        file = open('/home/wwh/Desktop/detect_track.txt','r')
        detect_track = file.read()
        file.close()
        print detect_track

        #detect
        if detect_track  == 'detect\n':
            demo_video(net,image)
            bbox = 1
        #track
        elif detect_track == 'track\n':
            print bbox
            if bbox == 1:
                print 'please selectROI'
                bbox = cv2.selectROI(image, False)
                ok = tracker.init(image, bbox)
                print 'ROI init success'
            if bbox != 1:
                # cv2.imshow('ret',image)
                cv2.waitKey(1)
                tracking(image,bbox)
            # Exit if ESC pressed
            k = cv2.waitKey(1) & 0xff
            if k == 27 : break
        #show iamge only
        elif detect_track == 'wait\n':
            write_picture_file(image)
            # cv2.imshow('ret',image)
            bbox = 1
        else:
            pass
