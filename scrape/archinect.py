import csv
import time
from urllib.request import urlopen

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from utils import extractEmail, extractEmailNormal


def scrapeSingle(url_ext, hunter):
    
    url = "https://archinect.com"
    page = urlopen(url+url_ext).read()
    soup = BeautifulSoup(page)
    
    if not soup.find("li", class_="Col1 SystemMessage"):
        contactDiv = soup.find("li", class_="Col1")
        try:
            tele = contactDiv.find("span", class_="TagIcon Phone").parent.find("span", class_="FixedWidth").get_text()
        except:
            tele = "x"
        try:
            web = contactDiv.find("span", class_="TagIcon Website").parent.a.get("href")
        except:
            web = contactDiv.find("i", class_="fal fa-laptop fa-stack-1x fa-inverse")
            if web is not None:
                web = web.parent.parent.get("href")
            else:
                web = url+url_ext
        try:    
            email = contactDiv.find("span", class_="TagIcon Email").parent.a.get("href")[7:]
        except:
            if hunter is not False:
                email = extractEmail(web, hunter)
            else: 
                email = extractEmailNormal(web)
        try:
            loc = contactDiv.p.get_text().replace("\r", "").replace("\n", "").replace("\t", "")
        except:
            loc = soup.find("div", class_="ColBProfile")
            if loc is not None:
                loc = loc.p.get_text()
        return { 
                'tele': tele,
                'web': web,
                'email': email,
                'loc': loc,
                }
    else:
        return { 
                'tele': "x",
                'web': "x",
                'email': "x",
                'loc': "x",
                }

def scrape(writing=False, hunter=False, soups=None):
    """ Encompasses archinect scrape for Ibiza
    
    Parameters
    ----------
    writing: bool
        Whether or not to write to temp.csv, if false it prints the rows
    """
    if writing:
        file = open('temp.csv', 'a+')
        writer = csv.writer(file)
        # writer.writerow(["Title", "Tele", "Email", "Web", "Addy", "Poblacion", "Position", "Contact Source", "Type", "More Info"])


    # get the page data and extract the links
    if soups is None:
        soups = selenium()
    
    for soup in soups:
        links = soup.find_all("a", class_="ThumbA")

        for link in links:
            # get the name of the firm
            title = link.get("title")
            # get the url_ext and do a single firm scrape
            url_ext = link.get("href")
            info = scrapeSingle(url_ext, hunter)
            # organize into columns


            row = [title, info['tele'], info['email'], info['web'], info['loc'], "Archinect", "Architecture / Design Firm", ""]

            if writing:
                writer.writerow(row)
                print("row written...")
            else:
                print(row)
                
    
    

def selenium():
    """ use selenium to get the html pages of the list of architects in a location
    
    Returns
    -------
    list(object)
        list of BeautifulSoup objects of the html page object
    
    """
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get("https://www.archinect.com/firms/search")
    time.sleep(5)
    driver.find_element_by_id("onesignal-slidedown-cancel-button").click()
    time.sleep(3)
    driver.find_element_by_id("location").send_keys("SPAIN")
    time.sleep(2)
    driver.find_element_by_id("location").send_keys(Keys.DOWN+Keys.DOWN+Keys.ENTER)
    radiusSearch = Select(driver.find_element_by_id("RadiusSearchSelect"))
    try:
        radiusSearch.select_by_value("100")
    except:
        pass
    driver.find_element_by_name("submit").click()
    
    soups = []
    # get page source
    el = driver.find_element_by_class_name("next")
    while el != None:
        html_source = driver.page_source
        data = html_source.encode('utf-8')
        soups.append(BeautifulSoup(data, 'lxml'))
        el.click()
        time.sleep(3)
        try:
            el = driver.find_element_by_class_name("next")
        except:
            el = None
    
    return soups
