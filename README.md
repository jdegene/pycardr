# pycardr
Search for a motive of an existing image on postcard selling websites.

Provide a folder containing at least 1 true image. pcardr will create a SQLite database, storing the images (and if wanted, automatically generated mutations of the image) and their dhash, phash, ahash and whash. It will then search various sites (possibly multiple search terms per site, which can be defined in a separate json file), retrieve all images and check their respective dhashes against each other. Lower dhash differences indicate more similar images (refer to [this](https://pypi.org/project/dhash/) repository for more information on image hashes).

All images with a dhash byte difference < 13 are stored as a possible match and images are downloaded for manual inspection. For all dhash byte differences < 10 a notification email is sent.

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

To make proper use of email notifications, either hardcode your info into sendMail() functions, or add a text file _Info.txt to the same folder of website_handling.py with 1 row containing username, 2nd row password, 3rd row Email adress to send to.

# how-to

1. Create a folder anywhere (this will be you working directory)
2. In you working directory, add:
	* a folder _img_raw_ - this contains the raw images to match
	* a folder _img_processed_ - this contains processed images from _img_raw_ folder (e.g. rotated...). This is filled using image_handling.img_prep()
	* a folder _im_pot_mactch_ - this will contain potential matching images found
	* optional a folder img_false - containing knowingly false images or images for testing purposes
	* a json file searches.json - keys are websites, entries are search queries to pass to this website later on
3. Run image_handling.py once (change working directory under __name__ == "__main__" first. This will initiate the SQLite database
4. Run individual functions in website_handling.py or use scheduler.py to run them all. Each function in website_handling.py handles the scraping of a specific site (or several country sites as in the case of ebay)
5. Wait for the results. Check _im_pot_mactch_ for potentially matching images, or wait for an email (see info under website_handling.py for this) with more likely matches, or manually check ahash, phash, whash values of all images in database. 