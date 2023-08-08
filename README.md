* credit goes to sd_hassan for the original script.
  
# what has changed:
  1. added in the ability to save to a directory.
  2. it will now pull up 200 images ( the max amount aloud per the civitai wiki.)
  3. will itterate through all the pages and download all those images.
  4. added in some error checking while dowloading the images. so now if it finds an image that error's out (" cannot write mode P as JPEG ") it will now show that url in the console, and continue on downloading the next image.

# some errors that you will see in the console.
  1. DecompressionBombWarning: see https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.open
  2. Error occurred on `https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/229fe8e5-b744-4d19-9e22-f366f16f5c88/width=512/229fe8e5-b744-4d19-9e22-f366f16f5c88.jpeg: cannot identify image file <_io.BytesIO object at 0x000001847C062E30>` ... (as an example.)
  3. Error occurred on `https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/edb375b8-e520-45f8-15ca-fad3a2b36100/width=2048/edb375b8-e520-45f8-15ca-fad3a2b36100.jpeg: cannot write mode P as JPEG` ... (as an example.)
 
# civitai-image-scraper
Downloads bulk images from Civitai that have a reaction count for a specific emoji reaction greater than your variable
Filters images in the response to only those that include a Prompt, saves the prompt as a caption text file matching the image name.
Outputted results are almost suitable for training. LORA's are included in prompts so to do is a toggle to remove LORA's from the saved text file, for now you can remove them manually if using this for training


# How to modify
Line 21, `directory = "civitai-images"` change to you directory.

Line 23, `parent_dir = "C:\\"` change to you Parent Directory path

Line 37, `api_key = "xxxxxxx"` change to your API key from Civitai account settings.

Line 78, `if image['stats']['heartCount'] > 10`

You can change the reaction type from heartCount to any other supported in the API 
At the time of this script creation, the supported reaction types are:

        "cryCount"

        "laughCount"
        
        "likeCount"
        
        "dislikeCount"
        
        "heartCount"
        
        "commentCount"
        
https://github.com/civitai/civitai/wiki/REST-API-Reference#get-apiv1images

# How to run
`pip install -r requirements.txt`

Replace line 37 API key with your API key

`python civitai-image-scraper.py`



# example![brave_0a4zJ0eXOn](https://user-images.githubusercontent.com/119671806/231275932-66eff47f-1073-4ce5-a0e4-c90b5ff8a145.gif)
