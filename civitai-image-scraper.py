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
import functools

# Define the threshold values for each statistic
reaction_counts = {
    'cryCount': (False, 1),        # Download images with >= 1 cry reactions
    'laughCount': (False, 1),      # Download images with >= 1 laugh reactions
    'likeCount': (False, 1),       # Download images with >= 1 like reactions
    'dislikeCount': (True, 20),    # Download images with >= 20 dislike reactions
    'heartCount': (False, 1),      # Download images with >= 1 heart reactions
    'commentCount': (False, 1),    # Download images with >= 1 comments
}

# Define the directory to save downloaded images
directory = "civitai-images"
parent_dir = "C:\\pictures-civitai-scrapped"  # Replace with your parent directory path

# Path for saving images and metadata
path = os.path.join(parent_dir, directory)

# Create the directory if it doesn't exist
try:
    os.makedirs(path, exist_ok=True)
    print("Directory '%s' created successfully" % directory)
except OSError as error:
    print("Directory '%s' can not be created" % directory)

# Replace with your API key
api_key = "xxxxxx"

# API endpoint
headers = {"Authorization": f"Bearer {api_key}"}

# Define page numbers for API requests
pages = np.arange(1, 99999, 200)

# List to store API responses
responses = []

# Create an error log file
error_log_filename = os.path.join(path, "error_log.txt")

# Create a file to store downloaded image IDs
dlimg_set = os.path.join(path, "downloaded_image_ID_DB.txt")

def download_image(image_info, dlimg_set_file=None, existing_image_ids=None):
    # Download and process an image
    image_id, image_url, image_meta = image_info

    if image_id in existing_image_ids:
        print(f"Skipped already downloaded image ID {image_id}")
        return 0  # Return 0 to indicate failure

    sanitized_image_id = re.sub(r'[^\w\-_.]', '_', str(image_id))
    img_filename = os.path.join(path, f"{sanitized_image_id}.jpg")
    meta_filename = os.path.join(path, f"{sanitized_image_id}_pos-prompt.txt")
    resources_filename = os.path.join(path, f"{sanitized_image_id}_resources.txt")
    negative_prompt_filename = os.path.join(path, f"{sanitized_image_id}_neg-Prompt.txt")

    try:
        img = download_image_from_url(image_url)
        save_image(img, img_filename)
        save_metadata(image_meta, meta_filename)
        save_resources(image_meta, resources_filename)
        save_negative_prompt(image_meta, negative_prompt_filename)

        if image_id is not None:
            add_to_existing_image_ids(image_id, existing_image_ids, dlimg_set_file)

        return 1  # Return 1 to indicate success
    
    except UnidentifiedImageError:
        print(f"UnidentifiedImageError for {image_url}: Unable to open image")
        return 0  # Return 0 to indicate failure
    
    except Exception as e:
        print(f"Error occurred on {image_url}: {e}")
        with open(error_log_filename, "a", encoding='utf-8') as error_log_file:
            error_log_file.write(image_url + '\n')
        return 0  # Return 0 to indicate failure

def download_image_from_url(image_url):
    # Download an image from a URL and convert it to RGB
    with warnings.catch_warnings(record=True) as warning_list:
        image_response = requests.get(image_url)
        img = Image.open(BytesIO(image_response.content))
    
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        elif img.mode == 'P' and 'transparency' in img.info:
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
        
        return img

def save_image(img, img_filename):
    # Save an image in JPEG format
    img.save(img_filename, "JPEG")

def add_to_existing_image_ids(image_id, existing_image_ids, dlimg_set_file):
    # Add downloaded image ID to the set and file
    existing_image_ids.add(image_id)
    with open(dlimg_set_file, "a", encoding='utf-8') as dlimg_set_file:
        dlimg_set_file.write(str(image_id) + '\n')

def save_metadata(image_meta, meta_filename):
    # Save image metadata
    if 'prompt' in image_meta:
        with open(meta_filename, "w", encoding='utf-8') as meta_file:
            meta_file.write(image_meta['prompt'])

def save_resources(image_meta, resources_filename):
    # Save image resources data
    resources_data = create_resources_data(image_meta)
    save_data_to_file(resources_data, resources_filename)

def create_resources_data(image_meta):
    # Create a formatted string for image resources data
    resource_fields = [
        'seed', 'Model', 'steps', 'sampler', 'cfgScale',
        'Clip skip', 'Mask blur', 'resources', 'Denoising strength',
        'SD upscale overlap', 'SD upscale upscaler'
    ]

    resources_data = "\n".join(f"{field}: {image_meta.get(field, 'N/A')}" for field in resource_fields)
    return resources_data

def save_negative_prompt(image_meta, negative_prompt_filename):
    # Save negative prompt data
    negative_prompt = image_meta.get('negativePrompt', 'N/A')
    save_data_to_file(negative_prompt, negative_prompt_filename)

def save_data_to_file(data, filename):
    # Save data to a file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(data)

def main():
    # Set up the warning filter to treat DecompressionBombWarning as an error
    warnings.simplefilter('error', UserWarning)
    
    # Calculate the total number of images to be processed
    total_images_to_process = sum(len(response.json()['items']) for response in responses)

    # Define the selected conditions based on user input
    selected_conditions = [
        lambda image: reaction_counts['cryCount'][0] and image['stats']['cryCount'] >= reaction_counts['cryCount'][1],
        lambda image: reaction_counts['laughCount'][0] and image['stats']['laughCount'] >= reaction_counts['laughCount'][1],
        lambda image: reaction_counts['likeCount'][0] and image['stats']['likeCount'] >= reaction_counts['likeCount'][1],
        lambda image: reaction_counts['dislikeCount'][0] and image['stats']['dislikeCount'] >= reaction_counts['dislikeCount'][1],
        lambda image: reaction_counts['heartCount'][0] and image['stats']['heartCount'] >= reaction_counts['heartCount'][1],
        lambda image: reaction_counts['commentCount'][0] and image['stats']['commentCount'] >= reaction_counts['commentCount'][1],
    ]

    # Load existing image IDs from the error log file
    existing_image_ids = set()
    if os.path.exists(dlimg_set):
        with open(dlimg_set, "r", encoding='utf-8') as dlimg_set_file:
            existing_image_ids = {line.strip() for line in dlimg_set_file}
    
    # Fetch images from the API with a limit of 200 images per page
    for page in pages:
        response = requests.get(
            'https://civitai.com/api/v1/images?cursor=' +
            str(page) +
            "&limit=200",
            headers=headers)
        responses.append(response)
    
    # Use ThreadPoolExecutor to parallelize image downloading and processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        image_infos = []  # Create an empty list to store image information
        dlimg_set_file = open(dlimg_set, "a", encoding='utf-8')  # Open the downloaded image ID file
        total_saved = 0  # Initialize the total_saved variable
        
        for response in responses:
            try:
                response_data = response.json()
                
                filtered_images = [
                    (image['id'], image['url'], image.get('meta', None))
                    for image in response_data['items']
                    if (
                        # print(f"Image {image['id']}:"),  # Debug print
                        image.get('meta') is not None  # Check if "meta" is not null
                        and all(cond(image) for cond in selected_conditions)  # Additional conditions
                        and (
                            not (
                                not (image['stats']['heartCount'] > 1) or not (image.get('meta') is not None) or not ('prompt' in image.get('meta', {})) or not image.get('meta', {}).get('prompt')
                            )
                        )
                    )
                ]
                
                # Add filtered image information to the list
                image_infos.extend(filtered_images)

                # Use ThreadPoolExecutor to concurrently download and process images
                download_partial = functools.partial(download_image, dlimg_set_file=dlimg_set_file, existing_image_ids=existing_image_ids)
                total_saved += sum(
                    tqdm(
                        executor.map(
                            download_partial,
                            image_infos,
                            chunksize=1),
                        total=total_images_to_process,
                        desc="Saving images and metadata",
                        unit="image"
                    )
                )
    
            except requests.exceptions.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Error: {e}")

    # Close the downloaded image ID file
    dlimg_set_file.close()
    
    # Print the total number of downloaded and saved images and metadata files
    print(
        f"Downloaded and saved {total_saved}/{len(image_infos)} images and metadata files."
    )   

if __name__ == "__main__":
    main()
