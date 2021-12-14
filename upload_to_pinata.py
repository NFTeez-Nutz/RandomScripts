#!/usr/bin/python3

import requests
import os
import json
import ast

METADATA_ONLY = True
PINATA_BASE_URL = 'https://api.pinata.cloud/'
ENDPOINT = 'pinning/pinFileToIPFS'
IMG_FORMAT = '.png'

# Change these to upload different files
filepath = '/home/user/project/art'
metadata_path = '/home/user/project/data/_metadata.json'

# Base directories for ipfs
img_base_dir = "art/"
data_base_dir = "data/"

# Upload Art
HEADERS = {'pinata_api_key': os.getenv('PINATA_API_KEY'),
           'pinata_secret_api_key': os.getenv('PINATA_API_SECRET')}

def upload_imgs(_filepath,_img_base_dir):
    def get_all_pngs(path):
        """get a list of absolute paths to every file located in the directory"""
        paths = []
        for filename in os.listdir(_filepath):
            if IMG_FORMAT in filename:
                paths.append(f"{_filepath}/{filename}")
        return paths

    paths = get_all_pngs(_filepath)
    files = [('file', _img_base_dir+file.split("/")[-1], open(file, "rb")) for file in paths]
    response = requests.post(PINATA_BASE_URL + ENDPOINT,
                            files=files,
                            headers=HEADERS)
    img_hash = response.json()['IpfsHash']
    print(f"img hash {img_hash}")

# Upload metadata
def upload_metadata(_metadata_path, _img_hash, _data_base_dir):
    tokens = []
    token_builder = ""
    # Stream file and jsonify each new json entry
    with open(_metadata_path, 'r') as f:
        for line in f: 
            open_count = 0 
            for ch in line:
                if ch == '{':
                    open_count += 1
                elif ch == '}':
                    open_count -= 1
                token_builder += ch

                # Check for start or end of token metadata
                if open_count == 0:
                    if ch in ['[',',']:
                        token_builder = ""
                        continue
                    if ch == '}':
                        tokens.append(' '.join(token_builder.split()))
                        token_builder = ""
                    elif ch == '{':
                        token_builder = "{"

    files = []
    for metadata in tokens:
        data = ast.literal_eval(metadata)
        id = data['edition']
        data['image'] = f"ipfs://{_img_hash}/{id}.png"
        files.append(('file', (_data_base_dir+f"{id}", json.dumps(data, indent=2).encode('utf-8'))))
    
    files.append(('file', (_data_base_dir+f"{id}", json.dumps(data, indent=2).encode('utf-8'))))
    response = requests.post(PINATA_BASE_URL + ENDPOINT,
                            files=files,
                            headers=HEADERS)
    data_hash = response.json()['IpfsHash']
    print(f"data hash {data_hash}")
    return data_hash

img_hash = ""    
if not METADATA_ONLY:
    img_hash = upload_imgs(filepath,img_base_dir)

if not img_hash:
    print("Please enter img hash")
else:
    upload_metadata(metadata_path, img_hash, data_base_dir)