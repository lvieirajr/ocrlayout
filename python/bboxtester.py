import io
import json
import logging
import os
import os.path
import sys
import types
import time
import requests

from enum import Enum
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import boto3 

try:
    from inspect import getfullargspec as get_arg_spec
except ImportError:
    from inspect import getargspec as get_arg_spec

# OCRLAYOUT Import
try:
    from ocrlayout.bboxhelper import BBOXOCRResponse,BBoxHelper,BBOXPoint
    print("PyPI Package imported")
except ImportError:
    print("Local Package imported")
    from ocrlayout_pkg.ocrlayout.bboxhelper import BBOXOCRResponse,BBoxHelper,BBOXPoint

# OCR Engines supported so far  
from testing.bboxtester_aws import AWSOCREngine
from testing.bboxtester_google import GoogleOCREngine
from testing.bboxtester_azure import AzureOCREngine, AzureReadEngine
from testing.bboxtester_utils import OCRUtils

# Inject a specific logging.conf for testing.
bboxhelper=BBoxHelper(customlogfilepath=os.path.join(os.path.dirname(os.path.realpath(__file__)), './bboxtester.conf'))

IMAGES_FOLDER = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "../images")

RESULTS_FOLDER = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "../tests-results")

ocrengines=[ AWSOCREngine("AWS",bboxhelper, IMAGES_FOLDER, RESULTS_FOLDER), GoogleOCREngine("Google",bboxhelper, IMAGES_FOLDER, RESULTS_FOLDER), AzureOCREngine("AZURE OCR",bboxhelper, IMAGES_FOLDER, RESULTS_FOLDER), AzureReadEngine("Azure READ",bboxhelper, IMAGES_FOLDER, RESULTS_FOLDER) ]


def iterate_all_images(ocrengines=[],filter=None,callOCR=True,verbose=False):
    """OCR Text detection for all images 
    Iterate through all images located in the IMAGES_FOLDER and call all OCR Engines
    """
    for filename in os.listdir(IMAGES_FOLDER):
        if filter:
            if filter not in filename:
                continue
        if '.DS_Store' in filename:
            continue
        imgfullpath=os.path.join(IMAGES_FOLDER, filename)

        p = Path(filename)
        (imgname,imgext) = os.path.splitext(p.name)
        if imgext not in '.pdf':
            OCRUtils.draw_cv2_boxes(image=imgfullpath,outputdir=RESULTS_FOLDER)

        for engine in ocrengines:
            engine.detect_text(imgfullpath, callOCR, verbose)


if __name__ == "__main__":
    import sys, os.path
    sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..", "..")))
    import os
    import argparse
    parser = argparse.ArgumentParser(description='Call OCR outputs for a given image or images dir')
    parser.add_argument('--image',type=str,required=False,help='Process a single image',default=None)
    parser.add_argument('--imagesdir',type=str,required=False,help='Process all images contained in the given directory',default=IMAGES_FOLDER)
    parser.add_argument('--filter',type=str,required=False,help='Filter the images to process based on their filename',default="")
    parser.add_argument('--outputdir',type=str,required=False,help='Define where all outputs will be stored',default=RESULTS_FOLDER)
    parser.add_argument('--callocr', dest='callocr', action='store_true',help='flag to invoke online OCR Service',default=False)
    parser.add_argument('-v','--verbose', dest='verbose', action='store_true',help='DEBUG logging level',default=False)
    args = parser.parse_args()

    # Output dir
    if args.outputdir:
        RESULTS_FOLDER=args.outputdir

    if not os.path.exists(RESULTS_FOLDER):
        os.makedirs(RESULTS_FOLDER)

    # Check for available OCR engine functions
    if len(ocrengines)==0:
        print("No OCR Engine found. exiting.")
        exit

    # Process a single image
    if args.image:
        if not os.path.exists(args.image):
            print("Image path doesn't exist.")
            exit
        else:
            for engine in ocrengines:
                engine.detext_text(filename=args.image,callOCR=args.callocr,verbose=args.verbose)
    else:
        if args.imagesdir:
            if not os.path.exists(args.imagesdir):
                print("Images folder doesn't exist.")
                exit
            else: 
                IMAGES_FOLDER=args.imagesdir
        # Process all images contained the IMAGES_FOLDER
        iterate_all_images(ocrengines=ocrengines,filter=args.filter,callOCR=args.callocr,verbose=args.verbose)
