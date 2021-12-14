#!/usr/bin/env python3

import os
import copy
from PIL import Image, ImageDraw, ImageFont

RESIZE_FACTOR = 1.5 # 1 = no change
input_path = "./input"
base = Image.open("canvas.png") # empty image with the target background size
for dir in os.listdir(input_path):
    dir_path = f"{input_path}/{dir}"
    for asset in os.listdir(dir_path):
        if ".png" not in asset:
            continue
        img = copy.copy(base)
        asset_img = Image.open(f"{dir_path}/{asset}")
        w,h = asset_img.size
        width = int(w*RESIZE_FACTOR)
        height = int(h*RESIZE_FACTOR)
        asset_img = asset_img.resize((width,height))
        img.paste(
            asset_img,
            (0,0), # x,y location of tr corner of asset_img on base
            asset_img)
        output_path = f"./output/{dir}"
        try:
            os.mkdir(output_path)
        except OSError as error:
            pass
        img.save(f"{output_path}/{asset}")