# -*- coding: utf-8 -*-

import json
from PIL import Image
import requests
from io import BytesIO

import image_handling
import website_handling

work_fol = 'D:/Stuff/Projects/bbeauty/'
conDB, c = image_handling.connect_db(work_fol + 'Database.sqlite')

# load json containing all search terms for each website
with open(work_fol + 'searches.json', 'r', encoding='utf8') as r:
  searchterm_json = json.load(r)


# # # # # # # # # # # # # # # # # # # #
# # # # # akpool.de # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # #

def get_AK(work_fol=work_fol, conDB=conDB, c=c, searchterm_json=searchterm_json):
    
    search_list = searchterm_json['AK']
    
    for search_term in search_list:
        
        cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
        existing_share = 0         
        
        while existing_share < 0.9:
            cur_page = cur_page + 1
            get_page = website_handling.AK(search_term, page=cur_page)
            
            if len(get_page) < 2:
                print("Leaving page, <2 items found")
                break 

            exisiting_imgs_int = 0 # how many imgs on site are already in DB

            # loop over every image on loaded site
            for image in get_page:
                
                # return 0 if image id is not in database yet
                imageID_found = image_handling.checkID(image['entry_id'], c, subsite='AK')
                exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
                existing_share = exisiting_imgs_int / len(get_page)
                
                if imageID_found == 0:
                    # load image url from web to PIL
                    img = Image.open(BytesIO(requests.get(image['thumb_url']).content))                

                    # cheack image's hashes against true images
                    lowest_dhash = image_handling.check_all_hashes(img, 
                                     (image['thumb_url'], image['entry_url'], 
                                      'AK', search_term, image['entry_id']), 
                                     work_fol,
                                     c, 
                                     conDB, 
                                     threshold=13)
                    
                    # send email notification for every image dHash < 10
                    if lowest_dhash < 10:
                        website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                      image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                      str(image['entry_id']))
                    
            print("Last page share was", existing_share)

                    
# # # # # # # # # # # # # # # # # # # #
# # # # # ansichtskartenversand.com # # 
# # # # # # # # # # # # # # # # # # # #

def get_AKV(work_fol=work_fol, conDB=conDB, c=c, searchterm_json=searchterm_json):

    search_list = searchterm_json['Ansichtskartenversand']
    
    for search_term in search_list:
    
        cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
        existing_share = 0 
        
        while existing_share < 0.9:
            cur_page = cur_page + 1
            get_page = website_handling.ansichtskartenversand(search_term, page=cur_page)
             
            if len(get_page) < 2:
                print("Leaving page, <2 items found")
                break
            
            exisiting_imgs_int = 0 # how many imgs on site are already in DB
             
            # loop over every image on loaded site
            for image in get_page:
                
                # return 0 if image id is not in database yet
                imageID_found = image_handling.checkID(image['entry_id'], c, subsite='AKV')
                exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
                existing_share = exisiting_imgs_int / len(get_page)
                
                if imageID_found == 0:
                    # load image url from web to PIL
                    img = Image.open(BytesIO(requests.get(image['thumb_url']).content))
                    
                    # cheack image's hashes against true images
                    lowest_dhash = image_handling.check_all_hashes(img, 
                                     (image['thumb_url'], image['entry_url'],
                                      'AKV', search_term, image['entry_id']), 
                                     work_fol,
                                     c, 
                                     conDB, 
                                     threshold=13)
                                     
                    # send email notification for every image dHash < 10
                    if lowest_dhash < 10:
                        website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                      image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                      str(image['entry_id']))
                
            print("Last page share was", existing_share)



# # # # # # # # # # # # # # # # # # # #
# # # # # delcampe.net  # # # # # # # # 
# # # # # # # # # # # # # # # # # # # #

def get_delcampe(work_fol=work_fol, conDB=conDB, c=c, searchterm_json=searchterm_json):
    
    search_list = searchterm_json['delcampe']
    
    for search_term in search_list:

        cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
        existing_share = 0 
        
        while existing_share < 0.9:
            cur_page = cur_page + 1
            get_page = website_handling.delcampe(search_term, page=cur_page)            
            
            if len(get_page) < 7: # account for top 6 non interesting thumbs
                print("Leaving page, <7 items found")
                break
            
            exisiting_imgs_int = 0 # how many imgs on site are already in DB            

            # loop over every image on loaded site
            for image in get_page:                 
                # return 0 if image id is not in database yet
                imageID_found = image_handling.checkID(image['entry_id'], c, subsite='delcampe')
                exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
                existing_share = exisiting_imgs_int / len(get_page)

                if imageID_found == 0:
                    # load image url from web to PIL
                    img = Image.open(BytesIO(requests.get(image['thumb_url']).content))

                    # cheack image's hashes against true images
                    lowest_dhash = image_handling.check_all_hashes(img, 
                                     (image['thumb_url'], image['entry_url'],
                                      'delcampe', search_term, image['entry_id']), 
                                     work_fol,
                                     c, 
                                     conDB, 
                                     threshold=13)

                    # send email notification for every image dHash < 10
                    if lowest_dhash < 10:
                        website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                      image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                      str(image['entry_id']))
            print("Last page share was", existing_share)
             
             
# # # # # # # # # # # # # # # # # # # #
# # # # #  ebay # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # #
  
def get_Ebay(work_fol=work_fol, conDB=conDB, c=c, searchterm_json=searchterm_json):

    # Step1: iterate all country specicif sites  
    for sub_site in ['de', 'com', 'co.uk', 'fr', 'com.au', 'ca', 'nl', 'it', 'es']:  
        search_list = searchterm_json['ebay.{}'.format(sub_site)]
        
        # Step2: Iterate over all related countries search terms
        for search_term in search_list:
    
            cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
            existing_share = 0 
            
            # Step3: proceed incrementing pages until >90% of images on a page are found in db
            while existing_share < 0.9:            
                cur_page = cur_page + 1
                get_page = website_handling.ebay(search_term, website=sub_site, page=cur_page)
                
                if len(get_page) < 2:
                    print("Leaving page, <2 items found")
                    break
                
                exisiting_imgs_int = 0 # how many imgs on site are already in DB
                
                # loop over every image on loaded site
                for image in get_page:
                    
                    # return 0 if image id is not in database yet
                    imageID_found = image_handling.checkID(image['entry_id'], c)
                    exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
                    existing_share = exisiting_imgs_int / len(get_page)
                    
                    if imageID_found == 0:
                        
                        # load thumbnail url from web to PIL
                        img = Image.open(BytesIO(requests.get(image['thumb_url']).content))
                        
                        # cheack image's hashes against true images
                        lowest_dhash = image_handling.check_all_hashes(img, 
                                         (image['thumb_url'], image['entry_url'],
                                          'ebay.{}'.format(sub_site), search_term, image['entry_id']), 
                                         work_fol,
                                         c, 
                                         conDB, 
                                         threshold=13)
                        
                        # send email notification for every image dHash < 10
                        if lowest_dhash < 10:
                            website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                          image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                          str(image['entry_id']))
                            
                print("Last page share was", existing_share)


# # # # # # # # # # # # # # # # # # # #
# # # # #  etsy.com/de  # # # # # # # #
# # # # # # # # # # # # # # # # # # # #

def get_etsy(work_fol=work_fol, conDB=conDB, c=c, searchterm_json=searchterm_json):
    search_list = searchterm_json['etsy']

    for search_term in search_list:
 
        cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
        existing_share = 0 
        
        while existing_share < 0.9:
            cur_page = cur_page + 1
            get_page = website_handling.etsy(search_term, page=cur_page)
            
            if len(get_page) < 1:
                print("Leaving page, <1 items found")
                break
            
            exisiting_imgs_int = 0 # how many imgs on site are already in DB  

            # loop over every image on loaded site
            for image in get_page: 

                # return 0 if image id is not in database yet
                imageID_found = image_handling.checkID(image['entry_id'], c, subsite='etsy')
                exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
                existing_share = exisiting_imgs_int / len(get_page)  

                if imageID_found == 0:
                    # load image url from web to PIL
                    img = Image.open(BytesIO(requests.get(image['thumb_url']).content))                    

                    # cheack image's hashes against true images
                    lowest_dhash = image_handling.check_all_hashes(img, 
                                     (image['thumb_url'], image['entry_url'],
                                      'etsy', search_term, image['entry_id']), 
                                     work_fol,
                                     c, 
                                     conDB, 
                                     threshold=13)
                    
                    # send email notification for every image dHash < 10
                    if lowest_dhash < 10:
                        website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                      image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                      str(image['entry_id']))          
            print("Last page share was", existing_share)



# # # # # # # # # # # # # # # # # # # #
# # # # #  google images  # # # # # # #
# # # # # # # # # # # # # # # # # # # #

def get_googleimgs(work_fol=work_fol, conDB=conDB, c=c, searchterm_json=searchterm_json):            
           
    search_list = searchterm_json['googleimgs']
    
    for search_term in search_list:
        cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
        existing_share = 0 

        #while existing_share < 0.9:
        cur_page = cur_page + 1
        get_page = website_handling.googleimages(search_term, page=cur_page)  

        exisiting_imgs_int = 0 # how many imgs on site are already in DB           

        # loop over every image on loaded site
        for image in get_page: 
            # return 0 if image id is not in database yet
            imageID_found = image_handling.checkID(image['entry_id'], c, subsite='googleimgs')
            exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
            existing_share = exisiting_imgs_int / len(get_page)   
            
            if imageID_found == 0:
                # load image url from web to PIL
                try:
                    img = Image.open(BytesIO(requests.get(image['thumb_url']).content))                     
                except:
                    #print(image['thumb_url'], "    failed")
                    continue
 
                # cheack image's hashes against true images
                lowest_dhash = image_handling.check_all_hashes(img, 
                                 (image['thumb_url'], image['entry_url'],
                                  'googleimgs', search_term, image['entry_id']), 
                                 work_fol,
                                 c, 
                                 conDB, 
                                 threshold=13)                   

                # send email notification for every image dHash < 10
                if lowest_dhash < 10:
                    website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                  image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                  str(image['entry_id'])) 
        
        print("Last page share was", existing_share)  
                  
# # # # # # # # # # # # # # # # # # # #
# # # # #  hippostcard.com  # # # # # #
# # # # # # # # # # # # # # # # # # # #

def get_hippostcard(work_fol=work_fol, conDB=conDB, c=c, searchterm_json=searchterm_json):
    
    search_list = searchterm_json['hippostcard']
    
    for search_term in search_list:
        cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
        existing_share = 0 

        while existing_share < 0.9:
            cur_page = cur_page + 1
            get_page = website_handling.hippostcard(search_term, page=cur_page)
            
            if len(get_page) < 1:
                print("Leaving page, <1 items found")
                break            

            exisiting_imgs_int = 0 # how many imgs on site are already in DB  

            # loop over every image on loaded site
            for image in get_page: 
                
                # return 0 if image id is not in database yet
                imageID_found = image_handling.checkID(image['entry_id'], c, subsite='hippostcard')
                exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
                existing_share = exisiting_imgs_int / len(get_page)                        

                if imageID_found == 0:
                    # load image url from web to PIL
                    img = Image.open(BytesIO(requests.get(image['thumb_url']).content)) 

                    # cheack image's hashes against true images
                    lowest_dhash = image_handling.check_all_hashes(img, 
                                     (image['thumb_url'], image['entry_url'],
                                      'hippostcard', search_term, image['entry_id']), 
                                     work_fol,
                                     c, 
                                     conDB, 
                                     threshold=13)
                                
                    # send email notification for every image dHash < 10
                    if lowest_dhash < 10:
                        website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                      image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                      str(image['entry_id']))  

            print("Last page share was", existing_share)



# # # # # # # # # # # # # # # # # # # #
# # # # #  oldpostcards.com # # # # # #
# # # # # # # # # # # # # # # # # # # #            

def get_oldpostcards(work_fol=work_fol, conDB=conDB, c=c, searchterm_json=searchterm_json): 
    
    search_list = searchterm_json['oldpostcards']

    for search_term in search_list:
        
        cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
        existing_share = 0 

        while existing_share < 0.9:
            cur_page = cur_page + 1
            get_page = website_handling.oldpostcards(search_term, page=cur_page)
            
            if len(get_page) < 2:
                print("Leaving page, <2 items found")
                break

            exisiting_imgs_int = 0 # how many imgs on site are already in DB
            
            # loop over every image on loaded site
            for image in get_page:           
            
                # return 0 if image id is not in database yet
                imageID_found = image_handling.checkID(image['entry_id'], c, subsite='oldpostcards')
                exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
                existing_share = exisiting_imgs_int / len(get_page)   
                
                if imageID_found == 0:
                    # load image url from web to PIL
                    img = Image.open(BytesIO(requests.get(image['thumb_url']).content))

                    # cheack image's hashes against true images
                    lowest_dhash = image_handling.check_all_hashes(img, 
                                     (image['thumb_url'], image['entry_url'],
                                      'oldpostcards', search_term, image['entry_id']), 
                                     work_fol,
                                     c, 
                                     conDB, 
                                     threshold=13)

                    # send email notification for every image dHash < 10
                    if lowest_dhash < 10:
                        website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                      image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                      str(image['entry_id']))
            
            print("Last page share was", existing_share) 

               
# # # # # # # # # # # # # # # # # # # #
# # # # #  oldthing.de  # # # # # # # #
# # # # # # # # # # # # # # # # # # # #

def get_oldthing(work_fol=work_fol, conDB=conDB, c=c, searchterm_json=searchterm_json):
    
    search_list = searchterm_json['oldthing']

    for search_term in search_list:
        
        cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
        existing_share = 0 

        while existing_share < 0.9:
            cur_page = cur_page + 1
            get_page = website_handling.oldthing(search_term, page=cur_page)
            
            if len(get_page) < 2:
                print("Leaving page, <2 items found")
                break

            exisiting_imgs_int = 0 # how many imgs on site are already in DB
            
            # loop over every image on loaded site
            for image in get_page:           
            
                # return 0 if image id is not in database yet
                imageID_found = image_handling.checkID(image['entry_id'], c, subsite='oldthing')
                exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
                existing_share = exisiting_imgs_int / len(get_page)            

                if imageID_found == 0:
                    # load image url from web to PIL
                    img = Image.open(BytesIO(requests.get(image['thumb_url']).content))
                    
                    # cheack image's hashes against true images
                    lowest_dhash = image_handling.check_all_hashes(img, 
                                     (image['thumb_url'], image['entry_url'],
                                      'oldthing', search_term, image['entry_id']), 
                                     work_fol,
                                     c, 
                                     conDB, 
                                     threshold=13)
                                     
                    # send email notification for every image dHash < 10
                    if lowest_dhash < 10:
                        website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                      image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                      str(image['entry_id']))
                                                  
            print("Last page share was", existing_share)


# # # # # # # # # # # # # # # # # # # #
# # # # #  postcardshopping # # # # # #
# # # # # # # # # # # # # # # # # # # #

def get_postcardshopping(work_fol=work_fol, conDB=conDB, c=c):
    ''' uses no search phrases, skims thtough entire collection '''
    
    cur_page = 0 # starting page to crawl (will instantly incremented by 1, so 0 is first page)
    existing_share = 0

    while existing_share < 0.9:
        cur_page = cur_page + 1
        get_page = website_handling.postcardshopping("", page=cur_page)
        
        if len(get_page) < 2:
            print("Leaving page, <2 items found")
            break

        exisiting_imgs_int = 0 # how many imgs on site are already in DB

        # loop over every image on loaded site
        for image in get_page:           
        
            # return 0 if image id is not in database yet
            imageID_found = image_handling.checkID(image['entry_id'], c, subsite='postcardshopping')
            exisiting_imgs_int = exisiting_imgs_int + min(imageID_found, 1)
            existing_share = exisiting_imgs_int / len(get_page) 

            if imageID_found == 0:
                # load image url from web to PIL
                img = Image.open(BytesIO(requests.get(image['thumb_url']).content))

                # cheack image's hashes against true images
                lowest_dhash = image_handling.check_all_hashes(img, 
                                 (image['thumb_url'], image['entry_url'],
                                  'postcardshopping', "", image['entry_id']), 
                                 work_fol,
                                 c, 
                                 conDB, 
                                 threshold=13)
                
                # send email notification for every image dHash < 10
                if lowest_dhash < 10:
                    website_handling.sendMail("dHash" + str(lowest_dhash) + "found. Check out \n" + 
                                                  image['thumb_url'] + "\n" +  image['entry_url'] + "\n" +  
                                                  str(image['entry_id']))

        print("Last page share was", existing_share)
        
"""
get_AK()
get_oldthing()
get_AKV()
get_Ebay()
get_delcampe()
get_hippostcard()
get_googleimgs()
get_oldpostcards()
get_postcardshopping()
"""

"""
get_etsy()
"""

























                