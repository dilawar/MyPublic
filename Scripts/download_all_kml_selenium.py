#!/usr/bin/env python
"""download_all_kml.py: 
Download all kml file.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
import os
baseUrl_ = 'http://egreenwatch.nic.in/Public/Reports/View_Download_KML.aspx'

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

profile = FirefoxProfile()
profile.set_preference("browser.download.panel.shown", False);
ftype = 'application/octet-stream'
profile.set_preference("browser.helperApps.neverAsk.openFile", ftype )
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", ftype)
profile.set_preference("browser.download.folderList", 2); 
profile.set_preference("browser.download.dir", "./");
profile.set_preference("browser.helperApps.alwaysAsk.force", False);
profile.set_preference("browser.download.manager.useWindow", False);

options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(firefox_options=options, firefox_profile=profile)

print("[INFO] Firefox Headless Browser Invoked")
import time

downloadBtnID = 'ctl00_ctl00_dpPH_dpPH_btnSearch'
tableId = 'ctl00_ctl00_dpPH_dpPH_gdCALs'
states_ = []
current_page_ = 1

def find_select_by_id( id ):
    global driver
    ss = driver.find_element_by_id( id )
    return Select(ss)

def download_from_table( table ):
    ds = table.find_elements_by_xpath( '//input[@text="Download"]' )
    for i, d in enumerate(ds):
        try:
            d.click()
            print( 'Downloadin by pressing button ID: %s' % d.get_attribute( 'id' ) )
        except Exception as e:
            print( 'Coud not click: %s' % e )
            pass


def download_kmp( state, siteType):
    global driver
    global states_
    driver.get( baseUrl_ )
    ss = find_select_by_id( "ctl00_ctl00_dpPH_dpPH_ddlState")
    states_ = [ o.text for o in ss.options ][1:]
    ss.select_by_visible_text( state )

    ss = find_select_by_id( 'ctl00_ctl00_dpPH_dpPH_ddlSiteType' )
    caTypes_ = [ o.text for o in ss.options ][1:]
    print( caTypes_ )
    ss.select_by_visible_text( siteType )

    submit = driver.find_element_by_id( 'ctl00_ctl00_dpPH_dpPH_btnSearch')
    submit.click()
    time.sleep(1)

    # now download verything on this page.
    #  pageLink = "javascript:__doPostBack('ctl00$ctl00$dpPH$dpPH$gdCALs','Page$%d')"
    table = driver.find_element_by_xpath( '//table[@id="%s"]' % tableId )
    download_from_table( table )

    return

    assert table, "Table not found"
    pages = table.find_elements_by_xpath( '//td/a' )

    #  print( table.get_attribute( 'innerHTML' ) )
    for p in pages:
        href = p.get_attribute( 'href')
        if 'Page$' not in href:
            continue
        try:
            print( 'Trying page', p )
            p.click()
        except Exception as e:
            print( e )
            continue

        continue

def main( ):
    global driver
    state = sys.argv[1]
    siteType = sys.argv[2]
    print( '[INFO]  State: %s, Site Type: %s' % (state, siteType))
    try:
        download_kmp( state, siteType)
    except Exception as e:
        print( e )
        driver.quit()

    driver.quit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print( 'CTRL+C' )
        driver.quit()
