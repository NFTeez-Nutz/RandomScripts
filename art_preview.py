#!/usr/bin/env python3

import copy
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool, Lock
import os
import time
import random

asset_path = "input/assets"
bg_path = "input/Base/Base.png"
fg_path = ""
img_out_path = f"./output/images"
start_id = 1
total_supply = 25

lock = None
assets = {}

# Multithreaded implementation
def startCreatingMulti(_max_processes=None):
    if not _max_processes:
        _max_processes = os.cpu_count()
    max_processes = _max_processes

    global lock
    lock = Lock()
    print('start creating NFTs.')

    for asset in os.listdir(asset_path):
        assets[asset] = [trait.split('.')[0] for trait in os.listdir(f"{asset_path}/{asset}")]

    # Start processes
    with Pool(max_processes) as pool:
        pool.map(creator, assets)

# Worker thread function
def creator(testAsset):
    print('-----------------')
    print(f'creating NFT {testAsset}')

    try:
        os.mkdir(f"{img_out_path}/{testAsset}")
    except OSError as error:
        pass

    bg_source = Image.open(bg_path)

    for testValue in assets[testAsset]:
        bg = copy.copy(bg_source)
        for asset in assets:
            value = testValue
            if asset != testAsset:
                rand = len(assets[asset])-1
                value = assets[asset][random.randint(0,rand)]
            layer = Image.open(f"{asset_path}/{asset}/{value}.png")
            bg.paste(
                layer,
                (0,0),
                layer
            )
        with lock:
            bg.save(f"{img_out_path}/{testAsset}/{testValue}.png")

def timer(f):
    start = time.time()
    f()
    end = time.time()
    return end-start

# Initiate code
doneFlag = "done.flag"
if os.path.exists(doneFlag):
    os.remove(doneFlag)
delta = timer(startCreatingMulti)
with open(doneFlag,'w') as f:
    f.write(f"Done in {delta} seconds")

    

