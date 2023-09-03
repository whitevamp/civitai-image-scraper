* even though very little remains of the origanal code. credit goes to sd_hassan for the original script
# I bring you version 2 and compleate rewrite to the script.

This document outlines the key changes and enhancements made in the second version of the Civitai Image Scraper script compared to the first version. These improvements aim to enhance performance, robustness, and functionality.

## Key Changes and Enhancements

1. **Multithreading for Concurrent Downloading:**
   The second script utilizes multithreading with the 'concurrent.futures' library, allowing concurrent downloading and processing of images and metadata. This significantly improves the overall speed of the scraping process.

2. **Enhanced Error Handling and Logging:**
   The enhanced script features comprehensive error handling for various exceptions, such as UnidentifiedImageError, ConnectionError, and other request-related errors. Detailed error logs are maintained for analysis and debugging.

3. **Support for Multiple Image Formats:**
   The script supports both JPEG and PNG image formats. Images are converted to RGB mode if necessary, and the appropriate format is chosen based on the image's attributes.

4. **Complete Metadata Storage:**
   In addition to saving the 'prompt' field, the enhanced script saves the entire 'meta' dictionary in a separate text file. This ensures that all available image metadata is captured and preserved.

5. **Modular and Readable Script Structure:**
   The script's structure has been reorganized for improved modularity and readability. Functions are organized logically, and detailed comments are provided to explain each section's purpose and functionality.

6. **Flexible Directory Structure:**
   The 'parent_dir' and 'directory' variable allows users to specify the directory where images and metadata will be saved. This provides flexibility in choosing the location of the downloaded files.

7. **downloaded image ID:**
   The script will now save the IDs of the images to a file so that when you run the file more then once, it will not redownload those files.

## Usage

To use the enhanced script, follow these steps:

1. Clone the repository.
2. Install dependencies from 'requirements.txt'.
3. Replace the 'api_key' variable with your Civitai API key. Line 37
4. Specify the desired directory in the 'directory' variable. Line 18
5. Specify the desired parent directory in the 'parent_dir' variable. Line 24
6. You can change the reaction type from heartCount to any other supported in the API.
    - Line 183 `if image['stats']['heartCount'] > 10`
     - At the time of this script creation, the supported reaction types are:
         ```
        "cryCount"
        "laughCount"
        "likeCount"
        "dislikeCount"
        "heartCount"
        "commentCount"
         ```
    - See [civitai API](https://github.com/civitai/civitai/wiki/REST-API-Reference#get-apiv1images) for more information  <br />

When I ran this script with a heart count of > 10 it generated:  
 - 14.6 GB and a file count of 167,668, including log files.  

7. Run the script and enjoy!  

## Credits

Original work by Hassan-sd. Enhancements and documentation by whitevamp.
