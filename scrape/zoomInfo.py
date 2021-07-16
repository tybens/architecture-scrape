import csv

from bs4 import BeautifulSoup
from selenium import webdriver

from utils import extractEmail, extractEmailNormal


def get_soups(BASE_URL):

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(BASE_URL)

    soups = []

    for i in range(5):
        save_source(driver, soups)
        if i == 0:
            # first page
            el = driver.find_element_by_class_name("pagination").find_element_by_class_name("arrowContainer")
            el.click()
            input("Have you clicked the bot checker?")
        else:
            # other pages
            el = driver.find_element_by_class_name("pagination").find_elements_by_class_name("arrowContainer")[1]
            el.click()

    return soups

def save_source(driver, soups):
    # save source after every click
    html_source = driver.page_source
    data = html_source.encode('utf-8')
    soups.append(BeautifulSoup(data))


def scrape(writing=False, hunter=False, soups=None):
    """ Scrapes zoominfo soups
    
    Parameters
    ----------
    writing: bool
        Whether or not to write to temp.csv, if false it prints the rows
    hunter: object
        The hunter api client  
    soups: list(object)
        List of bs4 objects to scrape
    """
    if writing:
        file = open('temp.csv', 'a+')
        writer = csv.writer(file)
        #writer.writerow(["Title", "Tele", "Email", "Web", "Addy", "Contact Source", "Type", "More Info"])
        
    if soups is None: return None
    
    i = 1
    for soup in soups:
        rows = soup.find("tbody").find_all("tr", class_="tableRow")

        for row in rows:
            company = row.find("div", class_="tableRow_companyName_nameAndLink").find_all("a")
            title = company[0].text
            web = company[1].text

            companyType = ", ".join([industry.text for industry in row.find("td", class_="industryData").find_all("li")])

            loc = row.find("td", class_="tableRow_locationInfo").text

            revenue = row.find('td', class_="tableRow_revenue").text
            employees = row.find('td', class_="tableRow_employees").text
            if hunter is not False:
                email = extractEmail(web, hunter)
            else:
                email = extractEmailNormal(web)
            data = [title, "", email, web, loc, "Zoominfo", companyType, f"revenue: {revenue}, employees: {employees}"]
            
            if writing: 
                writer.writerow(data)
                print(f"{i} written")
                i+=1
            else:
                print(data)
                