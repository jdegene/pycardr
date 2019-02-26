# -*- coding: utf-8 -*-

# Call file from windows scheduler to run automatic scraping
# Will put a log into the working folder

import json

import main_handler
import image_handling

import pendulum

work_fol = 'D:/Stuff/Projects/bbeauty/'
conDB, c = image_handling.connect_db(work_fol + 'Database.sqlite')

# load json containing all search terms for each website
with open(work_fol + 'searches.json', 'r', encoding='utf8') as r:
  searchterm_json = json.load(r)

# log string will keep log of run, write to file later
log_str = pendulum.now().to_datetime_string()  + " -- Database started with " + \
          str(c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]) + " entries\n"


# # RUN SITES, WRITE RESULTS TO log_str 


# AK
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_AK(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_AK() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before)+ "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_AK() FAILED" + "\n"           

# AKH
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_AKH(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_AKH() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before)+ "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_AKH() FAILED" + "\n"     

# AKV
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_AKV(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_AKV() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before)+ "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_AKV() FAILED" + "\n"

# cardcow
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_cardcow(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_cardcow() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before)+ "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_cardcow() FAILED" + "\n"     

# delcampe
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_delcampe(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_delcampe() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before)+ "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_delcampe() FAILED"  + "\n"

# Ebay
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_Ebay(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_Ebay() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before)+ "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_Ebay() FAILED"   + "\n"

# googleimages
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_googleimgs(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_googleimgs() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before)+ "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_googleimgs() FAILED"  + "\n"

# hippostcard
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_hippostcard(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_hippostcard() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before)+ "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_hippostcard() FAILED"  + "\n"


# oldpostcards
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_oldpostcards(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_oldpostcards() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before) + "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_oldpostcards() FAILED"  + "\n"

# oldthing
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_oldthing(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_oldthing() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before) + "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_oldthing() FAILED"  + "\n"

# postcardshopping
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_postcardshopping(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_postcardshopping() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before) + "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_postcardshopping() FAILED"  + "\n"

# todocoleccion
try:
    num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    main_handler.get_todocoleccion(work_fol=work_fol, conDB=conDB, c=c)
    num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_todocoleccion() successfully run, added lines: " + \
                         str(num_entries_after-num_entries_before) + "\n"
except:
    log_str = log_str + pendulum.now().to_datetime_string() + \
                         " - get_todocoleccion() FAILED"  + "\n"


# oldpostcards4sale.co.uk because it doesnt update very frequently
# etsy because etsy takes long, only get etsy every second day
if pendulum.now().day % 2 == 0:
    
    # oldpostcards4sale
    try:
        num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
        main_handler.get_oldpostcards4sale(work_fol=work_fol, conDB=conDB, c=c)
        num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
        log_str = log_str + pendulum.now().to_datetime_string() + \
                             " - get_oldpostcards4sale() successfully run, added lines: " + \
                             str(num_entries_after-num_entries_before) + "\n"
    except:
        log_str = log_str + pendulum.now().to_datetime_string() + \
                             " - get_etsy() FAILED"  + "\n" 
    # etsy
    try:
        num_entries_before = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
        main_handler.get_etsy(work_fol=work_fol, conDB=conDB, c=c)
        num_entries_after = c.execute('SELECT Count(*) FROM CrawlImgs').fetchone()[0]
        log_str = log_str + pendulum.now().to_datetime_string() + \
                             " - get_etsy() successfully run, added lines: " + \
                             str(num_entries_after-num_entries_before) + "\n"
    except:
        log_str = log_str + pendulum.now().to_datetime_string() + \
                             " - get_etsy() FAILED"  + "\n" 
  

with open(work_fol + '_log.txt', 'a') as w:
    w.write(log_str)

conDB.close()