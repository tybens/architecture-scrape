from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import argparse
import sys, csv, cfscrape
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from bs4 import BeautifulSoup

import time, re

def extractEmailNormal(url):
    """ This extracts emails from websites
    
    It checks the "mail-to" tag and returns the email, if none found
    we use regex to find all matching strings and return them.
    
    Parameters
    ----------
    url: str
        the url (ex: maca-archi.fr) of the website to search for emails
        
    Returns
    -------
    str
        a string of all the emails found, or an "x" if none found
        
    
    """
    EMAILEXCLUDE = ["leaflet", "example.com", "vue", "axios"]
    exp = re.compile(r"(?:.*?='(.*?)')")
    exp_email = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
    for ext in ["", "/contact",  "/contact-us", "/about", "/en/contact", "/contactos"]:
        try:
            try:
                page = urlopen("https://www."+url+ext).read()
            except URLError:
                page = urlopen("http://www."+url+ext).read()
                
            soup = BeautifulSoup(page)
            # Find any element with the mail icon
            for icon in soup.findAll("i", {"class": "icon-mail"}):
                # the 'a' element doesn't exist, there is a script tag instead
                script = icon.next_sibling
                # the script tag builds a long array of single characters- lets gra
                chars = exp.findall(script.text)
                output = []
                # the javascript array is iterated backwards
                for char in reversed(list(chars)):
                    # many characters use their ascii representation instead of simple text
                    if char.startswith("|"):
                        output.append(chr(int(char[1:])))
                    else:
                        output.append(char)
                # putting the array back together gets us an `a` element
                link = BeautifulSoup("".join(output))
                email = link.findAll("a")[0]["href"].replace("mailto:", "").replace("mail-to:", "")
                # the email is the part of the href after `mailto: `
                if email != None:
                    return email

            # uses simple regex to find emails
            emails = set(exp_email.findall(str(soup)))
            if len(emails) != 0:
                return " / ".join([x for x in filter(lambda x: any(i not in x for i in EMAILEXCLUDE), emails)])
        except (HTTPError, URLError):
            continue
    return "x"

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
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = f"https://www.architizer.com/firms/firm-location={COUNTRY}" if PROJECT else f"https://www.architizer.com/firms/project-location={COUNTRY}"
        self.verificationErrors = []
        self.accept_next_alert = True
    def scroll_scrape(self):
        driver = self.driver
        delay = 3
        driver.get(self.base_url)
        driver.find_element_by_link_text("Recommended").click()
        for i in range(1,80):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        html_source = driver.page_source
        data = html_source.encode('utf-8')
        soup = BeautifulSoup(data, 'lxml')
        return soup.find_all("a", class_="firm-name")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--COUNTRY", "-c", default="pt", type=str, help="str two letter country code. Only supports 'pt' and 'fr' and 'sp' for portugal and france and spain respectively")
    parser.add_argument("--PROJECT", "-p", default=0, type=int, help="Boolean for whether or not the location means to find companies that 'completed projects' in a location, 0 for false, 1 for true")
    args = parser.parse_args()
    COUNTRY = args.COUNTRY
    PROJECT = bool(args.PROJECT)
    if COUNTRY not in ["fr", "pt", 'sp']:
        raise "ArgumentError: country must be 'fr' or 'pt' or 'sp'"
    COUNTRYMAP = {'pt': "Portugal", 'fr': "France", 'sp': "Spain"}
    COUNTRY = COUNTRYMAP[COUNTRY]
    
    file = open('temp.csv', 'a+')
    writer = csv.writer(file)
    writer.writerow(["Title", "Tele", "Email", "Web", "Addy", "Poblacion", "Type"])
    
    sel = Sel()
    firms = sel.scroll_scrape()
    
    for i, firm in enumerate(firms):
        url_ext = firm['href']
        title = firm.get_text()
        info = architizerSpecificFirm(url_ext, hunter=False)
        # row needs to be 8 length [title, tele, email, web, location, source, studio type, more info]
        row = [title, info['tele'], info['email'], info['web'], info['loc'], "Archinect", info['studioType'], ""]
        writer.writerow(row)
        print(f"{i+1} rows written...")