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

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



def sendMail(contents):
    """ Send Email to notify probable findings"""
    
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
        subentry = entry.contents[0]
        img_url = subentry.find('a', {'class':'preview'}).contents[0]['src']
        if "?" in img_url:
            img_url = img_url[ : img_url.rfind('?') ]
        img_title = subentry.find('a', {'class':'preview'}).contents[0]['alt']
        
        article_url_short = subentry.find('a', {'class':'preview'})['href']
        article_url = 'https://www.ansichtskartenversand.com/ak/' + article_url_short[ : article_url_short.rfind('/?') ]
        
        img_id = getAKVIdFromUrl(article_url)
        
        entry_dict = {'entry_url': article_url, 'entry_id': img_id, 'thumb_url':img_url, 'text':img_title}
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
        
        thumb_url = 'https://www.hippostcard.com' + entry.find('img')['src']

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


















