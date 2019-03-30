# -*- coding: utf-8 -*-

# collection of website specific functions, that take the same arguments and return dictionaries
# containing urls and other info for found images per page

import smtplib
from email.message import EmailMessage
import json
import re
import requests
import urllib
import hashlib
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



def sendMail(contents):
    """ Send Email to notify probable findings"""
    
    try:
        uName = open('_Info.txt', "r").readlines()[0].rstrip('\n')
        uPass = open('_Info.txt', "r").readlines()[1].rstrip('\n')
        send_to = open('_Info.txt', "r").readlines()[2].rstrip('\n')
        
        server = smtplib.SMTP('smtp.web.de', 587)
        server.starttls()
        server.login(uName, uPass)
        
        msg = EmailMessage()
        msg.set_content(contents)
        msg['Subject'] = 'Image Notification'
        msg['From'] = uName
        msg['To'] = "You"
       
        # make sure username is the email address to send from
        server.send_message(msg, uName, send_to)
        server.close()
    except:
        print("MAIL SEND ERROR")


# # # ID Extraction Functions

def getAKVIdFromUrl(url):
    if url[-1] == '/':
        url = url[ : len(url) - 1]
    
    url_p1 = url[ url.rfind('/') + 1 : ]
    return_url = url_p1[ : url_p1.find('-') ]
    
    return return_url


def getEbayIdFromUrl(url):
    
    # especially on french site, the id is suddently prefixes by :m: instead of :g:
    if ':g:' in url:
        id_prefix = ":g:"
    else:
        id_prefix = ":m:"
    
    url_p1 = url[url.find(id_prefix) + 3 : ]
    
    if ':rk:' in url_p1:
        return_url = url_p1[ : url_p1.find(':')]
    else:
        return_url = url_p1
        
    return return_url


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
# MAIN WEBSITE FUNCTIONS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def AK(search_phrase, page=1):

    url = "http://www.akpool.de/suche/"+search_phrase.replace(" ", "%20") + "?page=" + \
            str(page) + "&sort_option=listed_in_shop_at+desc"
    
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    entries = soup.find_all('script', {'type': 'application/ld+json'})
    
    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site 
    for entry in entries:
        j = json.loads( entry.contents[0] )
        
        # json contains non product items, skip these
        if j['@type'] != 'Product':
            continue
    
        entry_dict = {'entry_url': j['url'], 'entry_id': j['sku'], 'thumb_url':j['image'], 'text':""}
        return_list.append(entry_dict)
        
    driver.close()
    return return_list



def ansichtskartenhandel(search_phrase, page=1):
    
    page_num = (page-1) * 25 
    url = "https://www.ansichtskartenhandel.at/de/?Params%5BCat%5D=0&Params%5BSearchInDescription"+\
          "%5D=0&Params%5BSearchParam%5D=" + search_phrase.replace(" ", "+") +\
          "&ItemSorting=8&aoff=" + str(page_num) + "&BrowseStartLimit="+ str(page_num) +\
          "&ItemSorting=8&ActionCall=WebActionArticleSearch"
    
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")   
    
    entries = soup.find_all('div', {'class': 'p_listing_box'})
    
    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site 
    for entry in entries:
        thumb_url = "https://www.ansichtskartenhandel.at" + entry.find("a").find('img')['src']
        entry_id = thumb_url[thumb_url.rfind("/") + 1 : -4]
        entry_url = "https://www.ansichtskartenhandel.at" + entry.find("a")['href']
        
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)

    driver.close()
    return return_list   


def ansichtskartenversand(search_phrase, page=1):
    
    if page == 1:
        url = "https://www.ansichtskartenversand.com/ak/index.php?search=standard&searchword=" + \
                search_phrase.replace(" ", "+") + "&id=0"
    else:
        url = "https://www.ansichtskartenversand.com/ak/index.php?search=standard&searchword=" + \
                search_phrase.replace(" ", "+") + "&id=0equal=1&start=" + str((page-1)*50 + 1)
                
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    entries = soup.find_all('div', {'class': lambda L: L and L.startswith('table-cards__row farbe')})
    
    
    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site 
    for entry in entries:    
        try:
            subentry = entry.contents[0]
            img_url = subentry.find('source')['srcset']
            if "?" in img_url:
                img_url = img_url[ : img_url.rfind('?') ]
            
            article_url_short = subentry.find('a', {'class':'preview'})['href']
            article_url = 'https://www.ansichtskartenversand.com/ak/' + article_url_short[ : article_url_short.rfind('/?') ]
            
            img_id = getAKVIdFromUrl(article_url)
        
        except:
            print("entry failed")
            continue
        
        entry_dict = {'entry_url': article_url, 'entry_id': img_id, 'thumb_url':img_url, 'text':""}
        return_list.append(entry_dict)
    
    driver.close()
    return return_list    


def antiquepostcardstore(page=1):
    
    url = "http://antiquepostcardstore.com/postcards/page/" + str(page) + "/?sort=newest"
    
    print(url, "loaded")
 
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")

    # get all entries containing images on site
    entries = soup.find_all("li", {"class" :  lambda L: L and L.startswith('product')})       

    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
        
        entry_url = entry.find('a')['href']
        
        try:
            thumb_url = entry.find('img')['src']
            thumb_url = thumb_url[ : thumb_url.find('?')]
        
            entry_id = thumb_url.split('/')[-2]
            
        except:
            print("no image for:", entry_url)
            continue

        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)    

    driver.close()
    return return_list   
    

def cardcow(search_phrase, page=1):
    
    url = "https://www.cardcow.com/search3.php?s=" + search_phrase.replace(" ", "+") + \
          "&section=unsold&sort=d&objects_per_page=200&page=" + str(page)

    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    entries = soup.find_all('div', {'class': lambda L: L and L.startswith('product-thumb-container')})    

    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site 
    for entry in entries:    
        thumb_url = 'https://www.cardcow.com' + entry.find('img')['data-src']
        entry_id = thumb_url[ thumb_url.rfind('/') + 1 : -4  ]        
        entry_url = 'https://www.cardcow.com' + entry.findNext('div').find('a')['href']
 
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)       

    driver.close()
    return return_list           


def catawiki(page=1, mode='crawl'):
    ''' bit different than other methods, as each entry can contain multiple postcards, so this process
    first collects all collections per site, then goes through each collection
    
    :mode: crawl = standard mode for image crawling, returns list of dicts with img infos
           max_site = used to extract info how many sites exist for postcards, returns one integer 
    
    '''
    
    # this just determines maximum no of pages and returns it as integer number
    if mode == 'max_site':
        url = 'https://www.catawiki.com/c/259-postcards'
        
        options = webdriver.firefox.options.Options()
        options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)   
                
        driver.get(url)    
        blankHTML = driver.page_source
        soup = BeautifulSoup(blankHTML, "html5lib")
        
        page_context = soup.find_all('span', {'class':'nav-link page'})
        
        driver.close()
        print("Starting catawiki, Maximum number of sites is:" + page_context[-1].text)
        return int(page_context[-1].text)
        
    # this is the normal img crawling mode
    else:
        url = 'https://www.catawiki.com/c/259-postcards?page=' + str(page)
        
        print(url, "loaded")
        
        options = webdriver.firefox.options.Options()
        options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)   
                
        driver.get(url)    
        blankHTML = driver.page_source
        soup = BeautifulSoup(blankHTML, "html5lib")
            
        # collect all main sites and add them to list
        main_sites_list = []
        entries = soup.find_all('article')
        for entry in entries:
            main_sites_list.append(entry.find('a')['href'])
        
        # collect all jpg links (one link per postcard) and add to return dictionary
        return_list = []
        for sub_url in main_sites_list:
            driver.get(sub_url)    
            sub_blankHTML = driver.page_source
            sub_soup = BeautifulSoup(sub_blankHTML, "html5lib")
        
            for pos_img_entry in sub_soup.find_all('a'):
                try:
                    if pos_img_entry['href'][-3:] == 'jpg':
                        thumb_url = pos_img_entry['href']
                    
                    entry_id = thumb_url[ thumb_url.rfind("-") + 1 : -4]
                    entry_dict = {'entry_url': sub_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
                    return_list.append(entry_dict) 
                    
                except:
                    pass
    
        driver.close()
        return return_list


def darabanth(page, search_phrase):
    """
    Search phrases require different behaviours, as some are for webshop, while others for live auction
    """
    
    if search_phrase in ['Topics_156997']:
        url = "https://webshop.darabanth.com/items/category/" + search_phrase+ "/page/" + str(page)
    else:
        url = "https://www.darabanth.com/de/fernauktion/343/kategorien~Ansichtskarten/" + search_phrase + "/?page=" + str(page)
    
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    if search_phrase in ['Topics_156997']:
        entries = soup.find_all('div', {'class': "tetel_tartalom"})
    else:
        entries = soup.find_all('div', {"class" : lambda L: L and L.startswith('item tetel_nezet_01')})
    
    
    return_list = []
    for entry in entries:
        
        # urls should work same for webshop and auction, but might fail due to error
        try:
            entry_url = entry.find('a', {'class': "gomb_barna"})['href']
            thumb_url = entry.find('img', {'class': "main_pic"})['src']
        except:
            continue
        
        # ids are referenced differently, first try/except is to distinguish which is which
        try:
            entry_id = entry.find('div', {'class': "cat_id"}).text
        except:
            try:
                entry_id =  entry.find('div', {'class': "tetel_id"}).find('font').text
            except:
                continue
        
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict) 

    driver.close()
    return return_list    



def delcampe(search_phrase, page=1):
    
    if page == 1:
        url = "https://www.delcampe.net/en_GB/collectables/search?search_mode=all&term=" + \
                search_phrase.replace(" ", "+")
    else:
        url = "https://www.delcampe.net/en_GB/collectables/search?search_mode=all&term=" + \
                search_phrase.replace(" ", "+") + "&page=" + str(page)
    
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    entries = soup.find_all('div', {'class': "item-gallery"})
    
    return_list = []
    for entry in entries:
        try:
            img_id = entry['id'] # skip item if it has no id in tag -> = top row thumbnails
        except:
            continue
    
        # get img thumbnail url. Site hides "nude" imgs, shows white png instead, skip these
        thumb_url = entry.find('img', {'class': "image-thumb"})["data-lazy"]
        if ".png" in thumb_url:
            continue
    
        article_url_short = entry.find('a', {'class': "item-link"})['href']
        article_url = "https://www.delcampe.net" + article_url_short
        
        entry_dict = {'entry_url': article_url, 'entry_id': img_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)
    
    driver.close()
    return return_list



def ebay(search_phrase, website='de', page=1):
    """
    Gets all product images on website, calls exactly one page
    Returns list containing dictionaries of image_id, image_url, thumbnail_url, image_name
    
    :website:       country identifier of url: de, com, co.uk.
    :search_phrase: phrase that is entered on website for searching
    :page:          page of search results to crawl
    
    """
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)    
    
    # build url to fetch, this will ensure sorting by date added + 100 hits per page
    if page==1:
        url = 'https://www.ebay.' + website + '/sch/i.html?_from=R40&_nkw=' + \
               search_phrase.replace(" ", "+") +'&_sacat=0&_sop=10&_ipg=100' 
    else:
        url = 'https://www.ebay.' + website + '/sch/i.html?_from=R40&_nkw=' + \
               search_phrase.replace(" ", "+") +'&_sacat=0&_sop=10&_ipg=100&_pgn=' + str(page)
    
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    print(url, "loaded")
    
    # get all entries containing images on site
    entries = soup.find_all("a", {"href" : lambda L: L and L.startswith('https://www.ebay.' + website + '/itm/')})
    
    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
                
        # every id is present twice, but only once with text, skip if not text/title version
        entry_txt = entry.text
        if len(entry_txt.strip()) < 10:
            continue

        
        entry_url = entry['href']
        entry_id = getEbayIdFromUrl(entry_url)  
        
        # entry_ids seem sometimes to be nonstandard, skip these
        #if len(entry_id) > 20:
        #    continue
        
        thumb_url = 'https://i.ebayimg.com/thumbs/images/g/' + entry_id + '/s-l225.jpg'            
        
        # dictionary to store each entries general information, only store if id not already present
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url, 'text':entry_txt}
        return_list.append(entry_dict)
      
    driver.close()
    
    # remove doublettes from return_list
    clean_return_list = []
    for x in return_list:
        clean_list_ids = [x['entry_id'] for x in clean_return_list]
        if x['entry_id'] not in clean_list_ids:
            clean_return_list.append(x)
    
    return clean_return_list


def etsy(search_phrase, page=1):
    
    if page == 1:
        url = "https://www.etsy.com/de/search?q=" + search_phrase.replace(" ", "+") + "&explicit=1&order=date_desc"
    else:
        url = "https://www.etsy.com/de/search?q=" + search_phrase.replace(" ", "+") + \
              "&explicit=1&order=date_desc&page" + str(page)

    print(url, "loaded")
 
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    # get all entries containing images on site
    #entries = soup.find_all("a", {"class" : lambda L: L and L.startswith('prolist display-inline-block listing-link')})   
    entries = soup.find_all("a", {"class" : re.compile(r'.inline-block listing-link.')})   
    
    return_list = []
    for entry in entries:
        entry_url = entry['href']
        entry_id = entry['data-listing-id']
        
        # main url does not seem to contain thumb url -> use main url to fetch sub-url with request -> grab jpg from there
        sub_site = requests.get(entry_url).text
        sub_soup = BeautifulSoup(sub_site, "html5lib")
        thumb_url = sub_soup.find('meta', {'property':"og:image"})['content']

        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)

    driver.close()
    return return_list


def falkensee(search_phrase, page=1):
    
    url = "https://www.antik-falkensee.de/catalog/index.php?cPath=" + search_phrase + "&sort=-1&page=" + str(page)
    
    print(url, "loaded")

    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib") 
    
    entries = soup.find("table", {"class" : "productListingData"}).find_all('tr')

    return_list = []
    for entry in entries:
        entry_url = ""
        for url_entries in entry.find_all('a'):            
            
            if '.jpg' in url_entries['href'].lower():
                thumb_url = url_entries['href'].lower()
                if thumb_url[:4] != 'http':
                    thumb_url = 'https://www.antik-falkensee.de/catalog/' + thumb_url
            
            elif len(entry_url) == 0 and 'product_info.php' in url_entries['href'].lower():
                entry_url = url_entries['href'].lower()
        
        entry_url = entry_url[ : entry_url.rfind('&') ]
        entry_id = entry_url[ entry_url.rfind('=') + 1 : ]
        
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)  

    driver.close()
    return return_list


def googleimages(search_phrase, page=1):
    """
    Google Images behaves special... it uses only first page of results, results are most important of current week
    entry_urls can point to aggregator sites, if these change they might not contain the found img anymore after a while
    """
    
    url = "https://www.google.com/search?q="+ search_phrase.replace(" ", "+") +"&safe=off&source=lnms&tbm=isch&tbs=qdr:w"
    
    print(url, "loaded")

    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")    
    
    # get all entries containing images on site
    entries = soup.find_all("a", {"jsname" : "hSRGPd"})   
    
    return_list = []
    for entry in entries:
        
        long_url = entry['href']
        if len(long_url) < 5:
            continue
        
        # find thumbnail url
        long_url_p1 = long_url[ long_url.find('imgurl=') + 7 : ]
        thumb_url_dec = long_url_p1[ : long_url_p1.find('.jpg') + 4 ]
        # url has to be decoded to utf8 first
        thumb_url = urllib.parse.unquote(thumb_url_dec)
        
        # find main url (might not necessarily be lowest level, eg ebay links might refer to search page)
        long_all_url_p1 = long_url[ long_url.find('imgrefurl=') + 10 : ]
        entry_url_dec = long_all_url_p1[ : long_all_url_p1.find('&') ]
        # url has to be decoded to utf8 first
        entry_url = urllib.parse.unquote(entry_url_dec)
        
        # google search uses md5 hash of thumburl as id
        entry_id = hashlib.md5(thumb_url.encode()).hexdigest()
        
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)        

    driver.close()
    return return_list



        
def hippostcard(search_phrase, page=1):

    url = "https://www.hippostcard.com/browse/?keywords=" + search_phrase.replace(" ", "+") + \
          "&limit=96&sort=started_desc&page=" + str(page)
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")    

    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "product-list grid"})  
    
    return_list = []
    for entry in entries:
        entry_url = entry.find('a')['href']
        
        entry_id_raw = entry.find('a')['id']
        entry_id = entry_id_raw[ entry_id_raw.find('-') + 1 :  ]
        
        thumb_url = entry.find('img')['src']
        
        # some urls reference link on hippostcard.com without domain prefix        
        if thumb_url.startswith("http") is False:
            thumb_url = 'https://www.hippostcard.com' + thumb_url

        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)
    
    driver.close()
    return return_list


def kartenplanet(search_phrase, page=1):
    
    url = "https://www.kartenplanet.ch/motive/" + search_phrase + "/?p=" + str(page)
    print(url, "loaded")   

    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")  

    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "box--content is--rounded"})  

    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
        entry_url = entry.find('a')['href']
        thumb_url = entry.find('img')['srcset']
        
        entry_id = entry_url[entry_url.find('Article/') + 8 : entry_url.rfind('/sCategory')]
        
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)            

    driver.close()
    return return_list


def lamasbolano(page=1):
    
    url = 'http://lamasbolano.com/tienda/9023-postales-antiguas?n=100&p=' + str(page) + '&orderby=date&orderway=desc&id_category=9023'
    
    print(url, "loaded")
 
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")

    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "center_block"})       

    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
        
        entry_url = entry.find('a')['href']
        thumb_url = entry.find('img')['src']
        
        entry_id_part1 = entry_url[entry_url.rfind('/') + 1 : ]
        entry_id = entry_id_part1[ : entry_id_part1.find("-")]

        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)    

    driver.close()
    return return_list


def liveauctioneers(page=1):
    url = "https://www.liveauctioneers.com/c/postcards/26573/?page=" + str(page) + "&pageSize=24&sort=-saleStart"
    
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    # collect all main sites and add them to list
    main_sites_list = []    
    entries = soup.find_all('div', {'class':'card___1ZynM cards___2C_7Z'})
    for entry in entries:
        main_sites_list.append(entry.find('a')['href'])

    # collect all jpg links (one link per postcard) and add to return dictionary
    return_list = []
    for sub_url in main_sites_list:        
        try:
            driver.get("https://www.liveauctioneers.com" + sub_url)    
        except:
            print(sub_url + "  passed")
            continue
        sub_blankHTML = driver.page_source
        sub_soup = BeautifulSoup(sub_blankHTML, "html5lib")
        
        # extract item id from sub_url
        sub_id = sub_url[ sub_url.find('item/') + 5 : sub_url.find('_')]
        
        # write all valid url to pix_url_list
        pic_url_list = []
        for pos_img_entry in sub_soup.find_all('img'):            
            try:
                # only add jpg links that contain sub_id
                if ('jpg' in pos_img_entry['src']) and (sub_id in pos_img_entry['src']):
                    pic_url = pos_img_entry['src']
                    pic_url = pic_url[ : pos_img_entry['src'].find('.jpg?')+4  ]
                    pic_url_list.append(pic_url)
            except:
                pass
            
        # remove duplicates from url_list
        pic_url_list = list(set(pic_url_list))
        
        for single_pic_url in pic_url_list:
            entry_dict = {'entry_url': sub_url, 'entry_id': sub_id, 'thumb_url':single_pic_url}
            return_list.append(entry_dict)

    driver.close()
    return return_list   


def mau_ak(search_phrase, page=1):
    
    url = "https://www.mau-ak.de/" + search_phrase + ".html?page=" + str(page) + "&listing_sort=6"

    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "product-item"}) 

    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
        entry_url = entry.find('a')['href']
        thumb_url = entry.find('img')['src']
        
        if thumb_url[:4] != 'hhtp':
            thumb_url = 'https://www.mau-ak.de/' + thumb_url
        
        entry_id = entry_url[ entry_url.rfind("-") + 1 :  entry_url.rfind(".") ] 

        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)    

    driver.close()
    return return_list


def oldpostcards(search_phrase, page=1):
    
    if page == 1:
        url = 'https://www.oldpostcards.com/' + search_phrase.replace(' ', '-') + '.html'
    else:
        url = 'https://www.oldpostcards.com/' + search_phrase.replace(' ', '-') + '-ss' + str(page) + '.html'

    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")

    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "prodimg"})     

    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
        
        entry_url = entry.find('a', {'href': lambda L: L and L.startswith('http')})['href']
 
        thumb_url = entry.find('a', {"class" : "vlightbox1"})['href']
        entry_id = thumb_url[ thumb_url.rfind('/') + 1 : -4  ]

        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)    

    driver.close()
    return return_list


def oldpostcards4sale(search_phrase, page=1):
    url = 'https://www.oldpostcards4sale.co.uk/search?page=' + str(page) + '&q=' + search_phrase
    
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "grid"}) 
    
    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
        # skip non postcard entries
        if len(entry) != 5:
            continue
        
        thumb_url = 'https://' + entry.find('a').find('img')['src'][2:]
        entry_url = entry.find('a')['href']
        entry_id = entry_url[entry_url.rfind('ref-') + 4 :]
        
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)
    
    driver.close()
    return return_list


def oldthing(search_phrase, page=1):
    
    if page == 1:
        url = "https://oldthing.de/Sammeln-und-Seltenes?sw=" + search_phrase.replace(" ", "%20") + "&ic=100"
    else:
        url = "https://oldthing.de/Sammeln-und-Seltenes?sw=" + search_phrase.replace(" ", "%20") + \
              "&ic=100&seite=" + str(page)

    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")
    
    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "row article-list-item"})   
    
    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
        entry_id = entry.attrs['data-article-id'] 
        
        subentry = entry.find('a')
        entry_url = "https://oldthing.de" + subentry['href']
        thumb_url = subentry.find('img')['src']
        
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)

    driver.close()
    return return_list
  

    
def philasearch(search_phrase, page=1):
    
    set_best = "&set_gesetz_bestaetigt_jn=J&gesetz_bestaetigt_neu=J"
    
    if "CPT" in search_phrase:
        url = "https://www.philasearch.com/de/dosearch.php?treeparent=GRP-15%" + search_phrase + "&page=" + str(page) + set_best
    else:
        url = "https://www.philasearch.com/de/tree_PCGRP-4/Sammlungen_und_Posten.html?page=" + str(page) + set_best
    
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")   

    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "card flex-container flex-dir-column"}) 
 
    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
        prefix = "https://www.philasearch.com"
        
        # if it doesnt have an url, consider entry as empty whitespace and skip
        try:
            entry_longurl = entry.find('a')['href']
        except:
            continue
        entry_url = prefix + entry_longurl[ : entry_longurl.rfind('breadcrumbId') - 1 ]
        
        thumb_url = entry.find('img')['src']
        
        entry_id = entry.find('span', {"data-block":"identifier"}).text[4:]

        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)        
    
    driver.close()
    return return_list        


def postcardshopping(search_phrase, page=1):
    '''search_phrase is ignored, entire collection is gone through'''    
    if page == 1:
        url = "http://www.postcardshopping.com/Merchant5/merchant.mvc?Screen=PLST" + \
              "&Store_Code=TPS&Category_Code=&Product_Code=&Search=&Per_Page=100&Sort_By=newest"
    else:
        offset = (page - 1) * 100
        url = "http://www.postcardshopping.com/Merchant5/merchant.mvc?Screen=PLST&" + \
              "AllOffset=" + str(offset) + "&Offset=" + str(offset) + "&Per_Page=100&Sort_By=newest"            
              
    print(url, "loaded")
    
    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")              

    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "column half medium-one-third category-product"}) 

    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site     
    for entry in entries:
        entry_url = entry.find('a')['href']
        thumb_url = 'http://www.postcardshopping.com/Merchant5/' + entry.find('img')['src']        
        entry_id = thumb_url[ thumb_url.rfind('/') + 1 : -4  ]

        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)
    
    driver.close()
    return return_list


def saleroom(page=1, mode='main', pass_list = []):
    """ mode main crawles main page, mode single a single item paged derived from main mode """
    
    if mode == 'main':
        url = "https://www.the-saleroom.com/en-gb/search-filter?"+\
              "searchterm=postcard&sortterm=publishedDate&page=" + str(page) + "&hasimage=True"
        
        print(url, "loaded")
    
        options = webdriver.firefox.options.Options()
        options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)   
                
        driver.get(url)    
        time.sleep(2)
        blankHTML = driver.page_source
        soup = BeautifulSoup(blankHTML, "html5lib")     
        
        # get all entries containing images on site
        entries = soup.find_all("div", {"class" : "lot-single"})  
        
        return_list = []
        # fill return_list with dictionaries containing urls, name, thumburls of images in site  
        for entry in entries:
            thumb_url = entry.find('img')['src']
            if "?" in thumb_url:
                thumb_url = thumb_url[ : thumb_url.rfind('?') ]
            entry_url = "https://www.the-saleroom.com" + entry.find('a')['href']
            entry_id = entry.find('img')['id']
            
            entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
            return_list.append(entry_dict)
        
        driver.close()
        return return_list
    
    
    elif mode == 'single':
        
        return_list = []
        for subsite_url in pass_list:
            options = webdriver.firefox.options.Options()
            options.add_argument('-headless')
            driver = webdriver.Firefox(options=options)   
                    
            driver.get(subsite_url)    
            time.sleep(2)
            blankHTML = driver.page_source
            soup = BeautifulSoup(blankHTML, "html5lib") 
            

            entries = soup.find_all("div", {"class" : "extra-images image slick-slide"})  
                                
            # fill return_list with dictionaries containing urls, name, thumburls of images in site  
            for entry in entries:
                
                thumb_url = entry.find('img')['src']
                if "?" in thumb_url:
                    thumb_url = thumb_url[ : thumb_url.rfind('?') ]
                entry_id = thumb_url[thumb_url.rfind('/') + 1 : -4]
                
                entry_dict = {'entry_url': subsite_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
                return_list.append(entry_dict)

        driver.close()
        return return_list                
  
    else:
        print("ERROR, UNKNOWN MODE. MODE CAN ONLY BE MAIN OR SINGLE")


def todocoleccion(website='postales-de-galantes-y-mujeres', page=1):
    
    url = 'https://www.todocoleccion.net/s/' + website + '?P=' + str(page)
    
    print(url, "loaded")

    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib")    
    
    # get all entries containing images on site
    entries = soup.find_all("div", {"class" : "lote-con-foto"})   

    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site  
    for entry in entries:
        
        entry_url = "https://www.todocoleccion.net" + entry.find('a')['href']
        
        thumb_url_long = entry.find('img')['data-original']
        thumb_url = thumb_url_long[ : thumb_url_long.find('.jpg')+4] # cutoff non interesting scaling part
    
        entry_id = entry_url[ entry_url.rfind('~') + 1 : ]

        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)

    driver.close()
    return return_list



def vintagepostcards(search_phrase, page=1):

    url = "https://www.vintagepostcards.com/catalogsearch/result/index/?p=" + str(page) + "&q=" + search_phrase.replace(" ", "+")

    print(url, "loaded")

    options = webdriver.firefox.options.Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)   
            
    driver.get(url)    
    blankHTML = driver.page_source
    soup = BeautifulSoup(blankHTML, "html5lib") 

    # get all entries containing images on site
    entries = soup.find_all("li", {"class" : lambda L: L and L.startswith('item') }) 

    return_list = []
    # fill return_list with dictionaries containing urls, name, thumburls of images in site  
    for entry in entries:
        entry_url = entry.find('a')['href']
        thumb_url = entry.find('img')['src']
        entry_id = entry_url[ entry_url.rfind('/') + 1 : -5 ]
        
        entry_dict = {'entry_url': entry_url, 'entry_id': entry_id, 'thumb_url':thumb_url}
        return_list.append(entry_dict)        

    driver.close()
    return return_list







