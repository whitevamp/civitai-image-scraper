import concurrent.futures
from io import BytesIO
import numpy as np
from PIL import Image
from PIL import UnidentifiedImageError
import os
import warnings
import requests
import re
from tqdm import tqdm
import json

##
# What's the directory name you want to save the downloaded images to.
directory = "civitai-images"

'''
What's the Parent Directory path. for windows it must contain \\ in the path.
IE: C:\\pictures-civitai-scrapped 
'''
parent_dir = "C:\\pictures-civitai-scrapped"

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

# Create an error log file
error_log_filename = os.path.join(path, "error_log.txt")

# DecompressionBombWarning log file.
dbwerror_log_filename = os.path.join(path, "DecompressionBombWarning_log.txt")

'''
Add downloaded image ID to the database, as we don't want to download the
same image twice. IE: we run the script once and then a week later we run it
once more, now with out this we would download that image again.
so all the image IDs are stored in a txt file and then read, on every run. 
'''
dlimg_set = os.path.join(path, "downloaded_image_ID_DB.txt")


def download_image(image_info, dlimg_set_file=None, existing_image_ids=None):
    image_id, image_url, image_meta = image_info

    if image_id in existing_image_ids:
        print(f"Skipped already downloaded image ID {image_id}")
        return 0  # Return 0 to indicate failure

    # Sanitize the image_id to remove characters that are not allowed in
    # filenames
    sanitized_image_id = re.sub(r'[^\w\-_.]', '_', str(image_id))

    img_filename = os.path.join(path, f"{sanitized_image_id}.jpg")
    meta_filename = os.path.join(path, f"{sanitized_image_id}.txt")

    try:
        with warnings.catch_warnings(record=True) as warning_list:
            image_response = requests.get(image_url)
            img = Image.open(BytesIO(image_response.content))
    
            if img.mode == 'RGBA':
                # Convert to RGB mode if image has an alpha channel
                img = img.convert('RGB')
                img_format = "PNG"
            elif img.mode == 'P' and 'transparency' in img.info:
                # Convert palette image with transparency to RGBA
                img = img.convert('RGBA')
                img_format = "PNG"
            else:
                # Convert other modes to RGB
                img = img.convert('RGB')
                img_format = "JPEG"
                # print(f"Image mode: {img.mode}")
                # print(f"Image size: {img.size}")
                # print(f"Image format: {img.format}")
                img.save(img_filename, img_format)  # Save the image
                
                # Save the "prompt" field.
                with open(meta_filename, "w", encoding='utf-8') as meta_file:
                    meta_file.write(image_meta['prompt'])
                '''
                # Instead of writing just the 'prompt' field,
                # write the whole 'meta' dictionary
                with open(meta_filename, "w", encoding='utf-8') as meta_file:
                    import json
                    json.dump(image_meta, meta_file, ensure_ascii=False, indent=4)
                 '''   
            # Add downloaded image ID to the set
            if image_id is not None:
                existing_image_ids.add(image_id)
                with open(dlimg_set, "a", encoding='utf-8') as dlimg_set_file:
                    dlimg_set_file.write(str(image_id) + '\n')
            
            return 1  # Return 1 to indicate success
    
    except UnidentifiedImageError:
        print(f"UnidentifiedImageError for {image_url}: Unable to open image")
        return 0  # Return 0 to indicate failure
    
    except Exception as e:
        print(f"Error occurred on {image_url}: {e}")
        with open(error_log_filename, "a", encoding='utf-8') as error_log_file:
            error_log_file.write(image_url + '\n')
        return 0  # Return 0 to indicate failure
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.ConnectionError):
            print(f'ConnectionError occurred on {image_url}: {e}')
            # Handle the ConnectionError here
        else:
            print(f'Error occurred on {image_url}: {e}')
            with open(error_log_filename, "a", encoding='utf-8') as error_log_file:
                error_log_file.write(image_url + '\n')
        return 0  # Return 0 to indicate failure
    
    # Handle the DecompressionBombWarning here
    except UserWarning as warning:
        if "DecompressionBombWarning" in str(warning):
            print(f'DecompressionBombWarning for {image_url}: {warning}')
            with open(dbwerror_log_filename, "a", encoding='utf-8') as dbwerror_log_file:
                dbwerror_log_file.write(
                    f'DecompressionBombWarning: {image_url}\n')
        return 0  # Return 0 to indicate failure


def main():
    # print("Entering main()")

    # Set up the warning filter to treat DecompressionBombWarning as an error
    warnings.simplefilter('error', UserWarning)
    
     # Load existing image IDs from the error log file
    existing_image_ids = set()
    if os.path.exists(dlimg_set):
        with open(dlimg_set, "r", encoding='utf-8') as dlimg_set_file:
            existing_image_ids = {line.strip() for line in dlimg_set_file}

    # Fetch images from the API with a limit of 200 images per page.
    for page in pages:
        # goto the webpage with a limt of 200 images per page.
        response = requests.get(
            'https://civitai.com/api/v1/images?cursor=' +
            str(page) +
            "&limit=200",
            headers=headers)
        responses.append(response)
        
    # Use ThreadPoolExecutor to parallelize image downloading and processing.
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        image_infos = []
        for response in responses:
            response_data = response.json()
            
            # Filter images based on specific conditions.
            filtered_images = [
                (image['id'],
                 image['url'],
                    image['meta']) for image in response_data['items'] if not (
                    not (
                        image['stats']['heartCount'] > 1) or not (
                        image['meta'] is not None) or not (
                        'prompt' in image['meta']) or not image['meta']['prompt'])]
            
            # Add filtered image information to the list.
            image_infos.extend(filtered_images)
             # Use ThreadPoolExecutor to concurrently download and process images.
        total_saved = sum(
            tqdm(
                executor.map(
                    lambda img_info: download_image(img_info, dlimg_set_file=dlimg_set_file, existing_image_ids=existing_image_ids),
                    image_infos),
                total=len(image_infos),
                desc="Saving images and metadata",
                unit="image"
            )
        )
    
    # Print the total number of downloaded and saved images and metadata files.
    print(
        f"Downloaded and saved {total_saved}/{len(image_infos)} images and metadata files."
    )   

if __name__ == "__main__":
    # print("Starting script")
    main()
    # print("Script finished")
