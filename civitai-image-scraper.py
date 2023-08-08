# Credit to Hassan-sd for orginal work.
# See the Readme for a list of all the changes.

import json
import os
from io import BytesIO
from random import randint
# from time import sleep

import numpy as np
import pandas as pd
import requests
from PIL import Image
from bs4 import BeautifulSoup
from requests import get
from tqdm import tqdm

# Image.MAX_IMAGE_PIXELS = None   # for DecompressionBombWarning

# whats the directory name you want to save the downloaded images to.
directory = "civitai-images"

# Parent Directory path
parent_dir = "C:\\"

# Path
path = os.path.join(parent_dir, directory)

# create a directory to place our images we recive.
try:
    os.makedirs(path, exist_ok=True)
    print("Directory '%s' created successfully" % directory)
except OSError as error:
    print("Directory '%s' can not be created" % directory)

# Replace with your API key
api_key = "xxxxxxxxx"

# API endpoint
headers = {"Authorization": f"Bearer {api_key}"}

# go to page 1 then stop at page 99999 and get 200 images at a time.
pages = np.arange(1, 99999, 200)  

# put the response into an array.
responses = []

# for loop for all the pages.
for page in pages:
    # goto the webpage with a limt of 200 images per page.
    response = requests.get(
        'https://civitai.com/api/v1/images?cursor=' +
        str(page) +
        "&limit=200",
        headers=headers)
    responses.append(response)


total_saved = 0  # outside of the loop

# Make API request
for response in responses:
    response_data = response.json()

    '''
	Filter images with stats.heartCount greater than 10 and a non-empty meta.prompt
	You can change the reaction type from heartCount to any other supported in the API At the time of this script creation, the supported reaction types are:
	"cryCount"
	"laughCount"
	"likeCount"
	"dislikeCount"
	"heartCount"
	"commentCount"
	'''
    # Filter images
    filtered_images = [
        image for image in response_data['items']
        if image['stats']['heartCount'] > 10 and image['meta'] is not None and 'prompt' in image['meta'] and image['meta']['prompt']
    ]

    # Download and save filtered images and metadata
    for image in tqdm(filtered_images, desc="Saving images and metadata", unit="image"):
        image_id = image['id']
        image_url = image['url']
        image_meta = image['meta']

        try:
            # Download image
            image_response = requests.get(image_url)
            img = Image.open(BytesIO(image_response.content))

            # Convert image to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Save image
            img_filename = f"{image_id}.jpg"
            img.save(os.path.join(path, img_filename), "JPEG")  # Changed file format to JPEG

            # Save meta.prompt as a text file
            meta_prompt = image_meta['prompt']
            meta_filename = f"{image_id}.txt"
            with open(os.path.join(path, meta_filename), "w", encoding='utf-8') as meta_file:
                meta_file.write(meta_prompt)

            total_saved += 1
        except BaseException as e:  # Capturing the specific exception
            print(f'Error occurred on {image_url}: {e}')

print(f"Downloaded and saved {total_saved}/{len(filtered_images)} images and metadata files.")
