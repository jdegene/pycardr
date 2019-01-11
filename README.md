# pycardr
Search for a motive of an existing image on postcard selling websites.

Provide a folder containing at least 1 true image. pcardr will create a SQLite database, storing the images (and if wanted, automatically generated mutations of the image) and their dhash, phash, ahash and whash. It will then search various sites (possibly multiple search terms per site, which can be defined in a separate json file, see below), retrieve all images and check their respective dhashes against each other. 

# files
* image_handling.py

Functions to handle everything related to image processing and database operations. All database writes are handles in here.
If run as file, it will create a new Database in work_fol (if non exists yet) and handles initial image loading. 

* main_handler.py

Manages how often and what pages of each website are called. Gets a list of image urls from website_handling.py and passes each indivual image to image_handling.py to compute hashes, check against True images in DB and save reference in database. 
	
* NoWindowScript.vbs
	
Is used to call run_bb.bat. The vbs script is only necessary to suppress the opening of a console window every time the scheduler would call run_bb.bat instead. Call this script from windows scheduler

* run_bb.bat 

batch file to execute scheduler.py script using the correct Python installation

* scheduler.py

File to call from Windows scheduler (in reality it is called through run_bb.bat, which is called by NoWindowScript.vbs). This is the highest level file. It adds the possibililty to run certain websites only for certain days (eg etsy takes long to crawl -> only run every second day). Also writes each successful/unsuccessful crawl attemp into a log file in work_fol
	
* website_handling.py	

Handles individual websites for scraping. Each function identically returns a list of dictionaries. One dictionary represents one crawled image, with info on a main_url, a thumbnail url and a unique id.