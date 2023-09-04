## Usage

To use the enhanced script, follow these steps:

1. Clone the repository.
2. Install dependencies from 'requirements.txt'. `pip install -r requirements.txt`
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
