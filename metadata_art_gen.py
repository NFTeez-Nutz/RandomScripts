#!/usr/bin/env python3

import json
import copy
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool, Lock
import os
import time

asset_path = "input/assets"
bg_path = ""
fg_path = ""
img_out_path = f"./output/images"
data_out_path = f"./output/metadata"
start_id = 1
total_supply = 10000

lock = None

# Multithreaded implementation
def startCreatingMulti(_max_processes=None):
    if not _max_processes:
        _max_processes = os.cpu_count()
    max_processes = _max_processes

    global lock
    lock = Lock()

    print('##################')
    print('# Generative Art')
    print('# - Create your NFT collection')
    print('###########')

    print()
    print('start creating NFTs.')

    ids = range(start_id, total_supply+start_id)

    # Start processes
    with Pool(max_processes) as pool:
        pool.map(creator, ids)


def getMetadata(id):
    metadata_path = "input/metadata"
    with open(f"{metadata_path}/{id}.json") as f:
        data = json.load(f)
        return data

# Worker thread function
def creator(id):
    print('-----------------')
    print(f'creating NFT {id}')

    bg_source = Image.open(bg_path)
    metadata = getMetadata(id)
    attributes = metadata['attributes']
    attributesMetadata = [a for a in attributes if 'Background' not in a['trait_type']]
    new_data = [{
        'new_data' : f'new hello'
    }]
    tempMetadata = {
            'dna': metadata['dna'],
            'name': f"new {metadata['name']}",
            'description': f"new {metadata['name']}",
            'image': f"{metadata['image']}",
            'edition': f"{metadata['edition']}",
            'attributes': new_data + attributesMetadata
        }
    bg = copy.copy(bg_source)
    for data in attributes:
        trait = data['trait_type']
        value = ''.join(data['value'].split())
		# Skip any traits
        if "Background" in trait:
            continue
		
        layer = Image.open(f"{asset_path}/{trait}/{value}.png")
        bg.paste(
            layer,
            (0,0),
            layer
        )
    # fg = Image.open(f"{fg_path}")
    # bg.paste(
    #         fg,
    #         (0,0),
    #         fg
    #     )
    with lock:
        bg.save(f"{img_out_path}/{id}.png")
        with open(f"{data_out_path}/{id}.json", 'w') as f:
                f.write(json.dumps(tempMetadata))

def timer(f):
    start = time.time()
    f()
    end = time.time()
    return end-start

# Initiate code
# startCreating()

doneFlag = "done.flag"
if os.path.exists(doneFlag):
    os.remove(doneFlag)
delta = timer(startCreatingMulti)
with open(doneFlag,'w') as f:
    f.write(f"Done in {delta} seconds")

    

