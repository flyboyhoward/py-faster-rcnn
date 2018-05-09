# readme

## introduction

Tools for training, testing, and compressing Fast R-CNN networks. Downloaded from [py-faster-rcnn](https://github.com/rbgirshick/py-faster-rcnn)

This code is modified for drone based car detection, key codes are uploaded in this repository.

Using CARPK dataset. Dataset details refer to https://lafi.github.io/LPN/

## usage

For training on another dataset, see https://github.com/deboc/py-faster-rcnn/tree/master/helpcarpk.py 

This repository is an example of one object detection. 

In this example, annotations is .txt form document, details refer to carpk_eval.py factory.py and CARPK_car folder.  

## file explanation 

demo.py read video stream from usbcamera

demo2.py read local video and display

demo1.py read local picture

For caffe make, see makefile.config.
