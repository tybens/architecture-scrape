import argparse
import csv
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import cfscrape
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (NoAlertPresentException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from utils import extractEmail, extractEmailNormal


def architizerSpecificFirm(url_ext, hunter):
    """ Scrapes the html of architizer's individual info page for a specific firm
    
    Parameters
    ----------
    url_ext : str
        the extension to the architizer.com base url (ex: "/brands/tech-lighting")
    hunter : object
        initialized pyhunter object to do the extracting
        
    Returns
    -------
    object
        Returns on object with parameters: studioType, tele, web, email, loc
    """
    
    base_url = "https://architizer.com"

    # scrape the page and make a bs object
    scraper = cfscrape.create_scraper()
    soup = BeautifulSoup(scraper.get(base_url+url_ext).content, "lxml")

    # get each info by parsing the html
    ## studio type
    studioTypeDiv = soup.find("div", class_="meta-row js-rendered-content")
    if studioTypeDiv is not None:
        studioType = studioTypeDiv.span.get_text()
    else:
        studioType = "x"
        
    ## telephone 
    rows = soup.find_all("span", class_="placeholder single-line")
    tele = ""
    for row in rows:
        text = row.get_text()
        if ":" in text:
            tele+=text+" / "
    if len(tele) != 0:
        tele = tele[:-3]
    else:
        tele = "x"
    ## website
    try:
        web = soup.find("a", "profile-website")['href'].replace("?utm_source=architizer", "")
    except:
        # if they don't have a website, link to the architizer site
        web = base_url+url_ext   
    ## email
    email = soup.find("span", "grey icon mail")
    if email is not None:
        email = email.parent.find("a")["href"].replace("mailto:", "").replace("mail-to:", "")
    elif "architizer" not in web:
        if hunter is not False:
            email = extractEmail(web, hunter)
        else: 
            email = extractEmailNormal(web)
            
    if email is not None:
        email = email if "@" in email else "x"
    else:
        email = "x"
    ## location
    try:
        loc = soup.find("span", "placeholder single-line js-rendered-content").get_text()
    except:
        loc = "x"
    
    return { 
            'studioType': studioType,
            'tele': tele,
            'web': web,
            'email': email,
            'loc': loc,
            }


class Sel:
    def __init__(self, COUNTRY, PROJECT, PROJECTTYPE):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = f"https://www.architizer.com/firms/firm-location={COUNTRY}{PROJECTTYPE}" if not PROJECT else f"https://www.architizer.com/firms/project-location={COUNTRY}{PROJECTTYPE}"
        self.verificationErrors = []
        self.accept_next_alert = True
    def scroll_scrape(self):
        driver = self.driver
        driver.get(self.base_url)
        driver.find_element_by_link_text("Recommended").click()
        for _ in range(1,80):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        html_source = driver.page_source
        data = html_source.encode('utf-8')
        soup = BeautifulSoup(data, 'lxml')
        return soup.find_all("a", class_="firm-name")


def scrape(COUNTRY, PROJECT, writing=False, hunter=False, PROJECTTYPE=""):
    
    if writing:
        file = open('temp.csv', 'a+')
        writer = csv.writer(file)
        writer.writerow(["Title", "Tele", "Email", "Web", "Addy", "Poblacion", "Type"])
    
    sel = Sel(COUNTRY, PROJECT, PROJECTTYPE)
    firms = sel.scroll_scrape()
    
    for i, firm in enumerate(firms):
        url_ext = firm['href']
        title = firm.get_text()
        info = architizerSpecificFirm(url_ext, hunter)
        # row needs to be 8 length [title, tele, email, web, location, source, studio type, more info]
        row = [title, info['tele'], info['email'], info['web'], info['loc'], "Archinect", info['studioType'], ""]
        
        if writing:
            writer.writerow(row)
        else:
            print(row)
        print(f"{i+1} rows written...")
