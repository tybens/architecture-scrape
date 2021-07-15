from urllib.request import urlopen
import csv

from bs4 import BeautifulSoup

def scrape(writing=False):
    url = "https://www.e-architect.com/spain/spanish-architect"
    html = urlopen(url)
    soup = BeautifulSoup(html, "lxml")
    
    # open and prepare to write to the file
    if writing:
        file = open('temp.csv', 'a+')
        writer = csv.writer(file)
    
    # get data
    rows = soup.find("table").find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        title = cols[0].get_text()
        tele = cols[1].get_text().replace("\n", " | ")
        info = cols[2].get_text().split("\n")
        email = info[0].replace("(at)", "@")
        if len(info) > 1:
            web = info[1]
        else:
            web = email
        loc = cols[3].get_text().replace("\n", "").replace(title, "")

        writeRow = [title, tele, email, web, loc, "e-architect", "Architecture Studio", ""]
        if writing: 
            writer.writerow(writeRow)
        else:
            print(writeRow)
        
        print("row written...")
