# -*- coding: utf-8 -*-

import os
import sqlite3
import numpy as np
import pendulum
from io import BytesIO
import requests

import pandas as pd

from PIL import Image
import imagehash
import cv2


def getAllImgIDs(cursor):
    ''' Returns a list of all image Ids in CrawledImage Table '''
    
    db_output = cursor.execute('SELECT img_id FROM CrawlImgs').fetchall()
    returnList = [x[0] for x in db_output]
    return returnList


def checkID(check_id, cursor, subsite=''):
    ''' Returns != 0 if check_id present in img_id and 0 if not present '''
    
    if len(subsite) == 0:
        db_output = cursor.execute('SELECT * FROM CrawlImgs WHERE img_id="{}"'.format(check_id)).fetchall()    
    else:
        db_output = cursor.execute('SELECT * FROM CrawlImgs WHERE img_id="{}" AND site="{}"'.format(check_id,subsite)).fetchall() 
    return len(db_output)
    

def hash_diff(hash1, hash2):
    '''
    Returns the integer Hash Difference between :hash1: and :hash2:
    Automatically converts stored text hashs to hex
    '''    
    if type(hash1) == str:
        hash1 = imagehash.hex_to_hash(hash1)
    if type(hash2) == str:
        hash2 = imagehash.hex_to_hash(hash2)
    
    return hash1-hash2


def connect_db(dbPath):
    '''
    Connects to SQLITE Database, creates empty one at :dbPath: if none exists
    '''
    
    # Test if db already exists, run inital table creation only if not
    if os.path.isfile(dbPath):
        dbExists = 1
    else:
        dbExists = 0
    
    # connect to SQLite3 DB and create cursor
    connectionDB = sqlite3.connect(dbPath)
    cursor = connectionDB.cursor()
    
    # Create new DB if none exists
    if dbExists == 0:
    
        # create table to store prepared images filepaths and their hashes
        cursor.execute('CREATE TABLE IF NOT EXISTS TrueImgs(filepath TEXT, aHash TEXT, dHash TEXT, pHash TEXT, wHash TEXT)')
        
        # create table to store random Test images filepaths and their hashes for testing
        cursor.execute('CREATE TABLE IF NOT EXISTS TestImgs(filepath TEXT, aHash TEXT, dHash TEXT, pHash TEXT, wHash TEXT)')
        
        # create table to store crawled images filepaths and their hashes
        cursor.execute('CREATE TABLE IF NOT EXISTS CrawlImgs(crawlDate TEXT,  \
                                                        img_Url TEXT, rel_Url TEXT, \
                                                        site TEXT, search_term TEXT, \
                                                        filepath TEXT, \
                                                        img_id TEXT, \
                                                        dHash TEXT, \
                                                        dhash_min INT, ahash_min INT, phash_min INT, whash_max INT)')
        
        # create table to store potential matches between 
        cursor.execute('CREATE TABLE IF NOT EXISTS PotMatch(crawlDate TEXT, filepath TEXT, truePath TEXT, rel_Url TEXT, \
                                                       aHash_diff INT, dHash_diff INT, pHash_diff INT, wHash_diff INT)')
        
        connectionDB.commit()
    
    return connectionDB, cursor
    


def fill_db(inFol, cursor, table):
    '''
    Write true images in folder into DB, calculating all hashes
    '''
    
    # get a list of existing files in DB
    existing_files = c.execute('SELECT filepath FROM TrueImgs').fetchall()
    
    for file_name in os.listdir(inFol):
        file_path = inFol + file_name
        img_file = Image.open(file_path)
        
        # skip if file has already been calculated and inserted in DB
        if (file_path,) in existing_files:
            continue
        
        aHash = str(imagehash.average_hash(img_file))
        dHash = str(imagehash.dhash(img_file))
        pHash = str(imagehash.phash(img_file))
        wHash = str(imagehash.whash(img_file))
        
        cursor.execute('INSERT OR IGNORE INTO ' + table + '  VALUES (?,?,?,?,?)', (inFol+file_name,aHash,dHash,pHash,wHash)) 



def img_prep(inFol, outFol):
    '''
    Transforms all images of :inFol: in various ways and saves them to :outFol:
    '''
    
    for file_name in os.listdir(inFol):
        
        # open image file and save a version of the original image in outFol
        file_path = inFol + file_name
        img_file = Image.open(file_path)
        
        # skip if image already exists -> assumes all image manipluations are present as well
        outfile_path = outFol + file_name[:-4] + "_"  + str(0) + ".jpg"

        if os.path.isfile(outfile_path):
            continue
        
        #img_file.save(outfile_path)
        
        # creates imgs with canvas in dirty white around image, size is relative to org image
        #for canvas in range(3,19,3):
        for rotation in range(0,271,90):
            
            img_rot = img_file.rotate(rotation, expand=True)
            img_rot.save(outFol + file_name[:-4] + "_"  + str(rotation) + ".jpg")
            
            # org image size and a derived canvas size
            #width, height = img_file.size        
            #canvas_mean_size = int( (width + height) / canvas)
            
            # create new empty image in dirty white and paste org image into it
            #empty_white_img = Image.new('RGB', (width+canvas_mean_size, height+canvas_mean_size), (232,232,232))
            #empty_white_img.paste(img_file, (int(canvas_mean_size/2),int(canvas_mean_size/2)) )
            
            # rotate image
            #empty_white_img_rot = empty_white_img.rotate(rotation, expand=True)
            
            # save canvased and rotated version, save a transposed version as well REMOVED
            #empty_white_img_rot.save(outFol + file_name[:-4] + "_" +  str(0) + "_" + str(rotation) + ".jpg")
            #empty_white_img_rot.transpose(Image.FLIP_TOP_BOTTOM).save(outFol + file_name[:-4] + "_" +  
            #                                                         str(canvas) + "_" + str(rotation) +
            #                                                         "flp.jpg")


def detect_rect(inImg, outPath=None):
    '''
    detect rectangles in image and crop image, returns a list of cropped PIL images with size >10% <90% of org image
    https://medium.com/coinmonks/a-box-detection-algorithm-for-any-image-containing-boxes-756c15d7ed26
    
    :inImg:  can be a filepath or a PIL image object
    :outPath: if not None, cropped images are saved to this folder
    '''
    
    # read image if inImg is a string = path
    if type(inImg) == str:
        img = cv2.imread(inImg, 0)
    # else assume PIL image, convert to array and reduce to single band
    else:
        # threw an error once, return only original img if error is thrown
        try:
            img = cv2.cvtColor(np.array(inImg), cv2.COLOR_BGR2GRAY)
        except:
            return [inImg]
    
    ratio = img.shape[1] / 600
    img = cv2.resize(img, (600, int(img.shape[0]/ratio))) 
    #img = cv2.resize(img, (0,0), fx=0.25, fy=0.25) 
    
    #thresh, img_bin = cv2.threshold(img, 100, 255,cv2.THRESH_BINARY|     cv2.THRESH_OTSU)
    thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
        cv2.THRESH_BINARY,11,2)
    
    # Invert the image
    img_bin = 255-thresh 
    
    # Defining a kernel length
    kernel_length = np.array(img).shape[1]//80
   
    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
    
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    
    
    # Morphological operation to detect vertical lines from an image
    img_temp1 = cv2.erode(img_bin, vert_kernel, iterations=3)
    verticle_lines_img = cv2.dilate(img_temp1, vert_kernel, iterations=3)
    
    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
    
    
    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha
    
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    thresh, img_final_bin = cv2.threshold(img_final_bin, 128,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)    
    
    # Find contours for image, which will detect all the boxes
    im2, contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    sub_img_list = []
    idx = 0
    for c in contours:
        # Returns the location and width,height for every contour
        x, y, w, h = cv2.boundingRect(c)
        if (w*h)/img.size > 0.1 and (w*h)/img.size < 0.9:
            
            # make subset of org image, convert array into PIL image file
            new_img = img[y:y+h, x:x+w]            
            new_img_pil = Image.fromarray(np.uint8(new_img))
            
            sub_img_list.append(new_img_pil)
            
            # save to outFol with date as a name
            if outPath is not None:
                #filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                filename = pendulum.now().to_datetime_string().replace(' ', '_').replace(':','-')
                cv2.imwrite(outPath + filename + str(idx) + '.jpg', new_img)
            
                idx += 1

    return sub_img_list
    #cv2.imshow('ImageWindow', new_img)
    #cv2.waitKey()



def check_all_hashes(inImg, infoTup, work_dir, cursor, connectDB, threshold=13):
    """
    Feeds an image to detect_rect() to harves all potential sub_images, calculates hashes for all
    Checks all hashes against DB entries and decides how to proceed with image
    
    :inImg: PIL image object
    :infoTub: Tuple containing info to write to DB (url, related_url, site, search_term, img_id)
    :work_dir: working directory, the directory must contain folder "img_pot_match" for output saving
    :cursor: DB cursor
    :connectDB: DB connections
    :threshold: if hash_difference < threshold -> image is considered potential match
    """
    
    img_list = detect_rect(inImg)
    img_list = [inImg] + img_list # put org image at beginning of list
    
    true_list = cursor.execute('SELECT filepath, aHash, dHash, pHash, wHash FROM TrueImgs').fetchall()
    
    min_hash_diff = 100
    
    for i, img in enumerate(img_list):

        img_dhash = imagehash.dhash(img)        
        for true_img in true_list:
            
            value = hash_diff(true_img[2], img_dhash)
        
            if value < min_hash_diff:
                min_hash_diff = value
                
                min_aHash = hash_diff(true_img[1], imagehash.average_hash(img))
                min_pHash = hash_diff(true_img[3], imagehash.phash(img))
                min_wHash = hash_diff(true_img[4], imagehash.whash(img))
                
                file_name = str(pendulum.now().timestamp()).replace(".","") + "_" + str(i)
                match_true = true_img[0]
                safe_dhash = str(img_dhash)
    
    # if there is part of the image that is below threshold, save main img to folder and put info in PotMatch table
    output_file = ""
    if min_hash_diff < threshold:
        output_file = work_dir + 'img_pot_match/' + file_name + ".jpg"
        img_list[0].save(output_file, "JPEG")       

        cursor.execute('INSERT OR IGNORE INTO PotMatch VALUES (?,?,?,?,?,?,?,?)', (pendulum.now().to_datetime_string(),
                                                                               output_file, 
                                                                               match_true,  
                                                                               infoTup[1],
                                                                               min_aHash,
                                                                               min_hash_diff,
                                                                               min_pHash,
                                                                               min_wHash)) 

    # write basic infos for each crawled file into SQLite
    cursor.execute('INSERT OR IGNORE INTO CrawlImgs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (pendulum.now().to_datetime_string(), 
                                                                      infoTup[0],                                                                             
                                                                      infoTup[1],
                                                                      infoTup[2],
                                                                      infoTup[3],
                                                                      output_file,
                                                                      infoTup[4],
                                                                      safe_dhash,
                                                                      min_hash_diff,
                                                                      min_aHash,
                                                                      min_pHash,
                                                                      min_wHash))

    connectDB.commit()
    return min_hash_diff
    


def test_hashes(cursor, test_val, test_hash):
    '''
    Test all images in TrueImgs vs. all images in TestImgs
    
    :test_val: threshold value to count as identical image
    :test_hash: int 1-4 to indicate which hash to check (1=a, 2=d, 3=p, 4=w)
    '''
    
    true_list = cursor.execute('SELECT filepath, aHash, dHash, pHash, wHash FROM TrueImgs').fetchall()
    test_list = cursor.execute('SELECT filepath, aHash, dHash, pHash, wHash FROM TestImgs').fetchall()
    
    ret_list = []
    
    # match every img with every img and every hash
    for true_img in true_list:
        for test_img in test_list:
            for hashx in range(1,5):
                value = hash_diff(true_img[hashx], test_img[hashx])
                
                if (value <= test_val) and (hashx == test_hash):
                    print( true_img[0], "\n",
                           test_img[0], "\n",
                           hashx, value )
                    ret_list.append((true_img[0], test_img[0], value))
    
    return ret_list



def get_best_of_the_rest(db_connection, 
                         hash_type = 'all_non_d',
                         start_date = '', 
                         end_date = pendulum.now().to_date_string(),
                         outFol = '',
                         get_top = 100):
    '''
    Downloads the best hits over a certain period of time. Best hits can be mean of hashes.
    
    :db_connection: a database connection, output of connect_db
    :outFol: folder to save output jpegs to, create folder for this first
    :get_top: how many best values to download
    
    :hash_type: can be either all_non_d (3 hashes, without dhash, default), all (4 hashes), 
        ahash, dash, phash, whash
    '''
    
    if start_date == '' or outFol == '':
        print('Enter start_date or output folder')
        return
    
    # get all data from sqlite into dataframe
    sql_query =  "SELECT * FROM CrawlImgs".format(start_date,end_date)
    db_df = pd.read_sql(sql_query, db_connection)
    
    # filter dataframe by date, create new col to sum requested hash columns
    db_df = db_df[ (db_df['crawlDate'] >= start_date) & (db_df['crawlDate'] >= end_date)]
    
    if hash_type == 'all_non_d':
        db_df['hash_sum'] = db_df['ahash_min'] + db_df['phash_min'] + db_df['whash_max']
    elif hash_type == 'all':
        db_df['hash_sum'] =  db_df['dhash_min'] + db_df['ahash_min'] + db_df['phash_min'] + db_df['whash_max']
    else:
        db_df['hash_sum'] =  db_df[hash_type]
        
    # sort values by caluclated hash_sum, get url list of top values (lowst values)
    db_df_sorted = db_df.sort_values('hash_sum')
    
    for img_entry in db_df_sorted.iloc[:get_top].iterrows():
        img = Image.open(BytesIO(requests.get(img_entry[1]['img_Url']).content))
        img.save(outFol + str(img_entry[1]['hash_sum']) + '_' + str(img_entry[1]['img_id']) + '.jpg')
        

if __name__ == "__main__":
    
    work_fol = 'D:/Stuff/Projects/bbeauty/'        
    conDB, c = connect_db(work_fol + 'Database.sqlite')
    
    # run this to get best of the rest
    get_best_of_the_rest(conDB, hash_type = 'all_non_d', start_date = '2019-01-10', 
                         end_date = pendulum.now().to_date_string(),
                         outFol = work_fol + 'img_bestoftherest/',
                         get_top = 100)
    
    # run these two if no database existed yet
    #img_prep(work_fol + "img_raw/", work_fol + "img_processed/")
    #fill_db(work_fol + 'img_processed/', c, 'TrueImgs')
    
    # Optional, for testing purposes of known false images
    #fill_db(work_fol + 'img_false/', c, 'TestImgs')
    
    conDB.commit()
    conDB.close()





# TESTBENCH
"""
img1_path = 'D:/Stuff/Projects/bbeauty/img_raw/8ztVSdX.jpg'
img1a_path = 'D:/Stuff/Projects/bbeauty/img_raw/8ztVSdX_2.jpg'
img2_path  = 'D:/Stuff/Projects/bbeauty/img_raw/Card1.jpg'


fimg1 =  'D:/Stuff/Projects/bbeauty/img_false/Alison.jpg'
fimg2 =  'D:/Stuff/Projects/bbeauty/img_false/s-l500.jpg'
fimg3 =  'D:/Stuff/Projects/bbeauty/img_false/NMH.jpg'



image1 = Image.open(img1_path)
image1a = Image.open(img1a_path)
image2 = Image.open(img2_path)



fimage1 = Image.open(fimg1)
fimage2 = Image.open(fimg2)
fimage3 = Image.open(fimg3)

i1 = imagehash.dhash(image1)
i1a = imagehash.dhash(image1a)
i2 = imagehash.dhash(image2)
i4 = imagehash.dhash(image4)

fi1 = imagehash.dhash(fimage1)
fi2 = imagehash.dhash(fimage2)
fi3 = imagehash.dhash(fimage3)


ai1 = imagehash.average_hash(image1)
ai1a = imagehash.average_hash(image1a)
ai2 = imagehash.average_hash(image2)

afi1 = imagehash.average_hash(fimage1)
afi2 = imagehash.average_hash(fimage2)
afi3 = imagehash.average_hash(fimage3)


croppedIm = image2.crop((-200, -200, 565, 560))



for images in os.listdir('D:/Stuff/Projects/bbeauty/img_false/'):
    theimg = Image.open('D:/Stuff/Projects/bbeauty/img_false/' + images)
    check_all_hashes(theimg, ("url.de", "ebay.de/123/postx" , "Hans.jpg", "hans_site", "xxx"), 'D:/Stuff/Projects/bbeauty/', c, conDB, threshold=13)



def detect_rect_old():
    '''
    detect rectangles in image, assume smallest rectangle is postcard for cropping
    '''
    
    #load image with PIL, resize, make grayscale, convert to openCV
    image = Image.open('D:/Stuff/Projects/bbeauty/img_raw/8ztVSdX.jpg')
    #width, height = image.size 
    #factor = width / 300
    #image_res_bw = image.resize((300, int(height/factor) )).convert(mode = "L")    
    #open_cv_image =  np.array( image_res_bw )
    #plt.imshow(open_cv_image,cmap='gray')
    
    image_bw = image.convert(mode = "L")  
    open_cv_image =  np.array( image_bw )
    
    kernel = np.ones((5,5),np.uint8)
    erosion = cv2.erode(open_cv_image,kernel,iterations = 2)
    kernel = np.ones((4,4),np.uint8)
    dilation = cv2.dilate(erosion,kernel,iterations = 2)
    
    edged = cv2.Canny(open_cv_image,10, 200)
  
    
    # threshold resized image (convert to black/white for certain gaussian threshold)
    thresh = cv2.adaptiveThreshold(open_cv_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)
    
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # loop over the contours
    for c in cnts:
    	# compute the center of the contour, then detect the name of the
    	# shape using only the contour
    	M = cv2.moments(c)
    	cX = int((M["m10"] / M["m00"]) * factor)
    	cY = int((M["m01"] / M["m00"]) * factor)
    	shape = sd(c)
     
    	# multiply the contour (x, y)-coordinates by the resize ratio,
    	# then draw the contours and the name of the shape on the image
    	c = c.astype("float")
    	c *= factor
    	c = c.astype("int")
    	cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
    	cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
    		0.5, (255, 255, 255), 2)
     
    	# show the output image
    	cv2.imshow("Image", image)

#plt.imshow(cnts[2])

"""