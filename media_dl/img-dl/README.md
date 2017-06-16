
Download Images 
=
 
### Script Design
----------------- 
(1) downloadImg2.py 
- This file contains core-functions to parse textfile.txt and download images from links.

(2) start.py
- This file is a start-script, contains parameters (path to textfile and save location), input by Users.

(3) multiDownloadImg.py
- download images from webpage

(3) textfile.txt
- All images delivered from the links inside this file are only used for functional testing purpose of the script. All these images currently already have public access and their copyright belong to the owner of website/ links where images have been uploaded.

(4) multiDownloadYT.py
- download files from youtube

(5) youtube.txt
- Create file youtube.txt (ex. touch youtube.txt) and copy all video-urls into this file (one line one url) 
(ex. youtube.com and copy video-url & paste here)

### Preparation
---------------

(1) Prerequisites:
- pip (check version of pip and upgrade it if possible)        
    > pip --version
    > pip install --upgrade pip

- it's recommended to test this script in virtual environment:
    > pip install virtualenv

(2) Dependencies:
- use virtualenv to create test environment:
    > virtualenv try_download_image
- activate virtual environment:
    > . try_download_image/bin/activate 
- install dependencies:
    > python setup.py install

(3) for download video files from youtube:
- need avconv at least version 10 from libav-tools
    > sudo apt-get install youtube-dl
    
### Run the script 
------------------
 

    - get help information
        > ./start.py -h   

    - run script, example:
        > ./start.py -links path_to_text_file.txt -save path_to_save_location   
        > (example: ./start.py -links /home/lphan/textfile.txt -save ../localsave/ )

        > ./start.py -u url_link_of_image -save path_to_save_location
        > (example: ./start.py -u http://link.jpg -save ../localsave/ )

        > ./start.py -w url_webpage -save path_to_save_location
        > (example: ./start.py -w 'http://www.domaintest.com' -s '../localsave/ )

        > python multiDownloadYT.py 
        > (file youtube.txt must be at the same location as multiDownloadYT.py containing video-urls) 
