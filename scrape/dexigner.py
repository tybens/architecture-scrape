import csv
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from bs4 import BeautifulSoup

from utils import extractEmail, extractEmailNormal


def scrape(urls, writing, studios_we_care_about, hunter=False):
    """ This scrapes the www.dexigner.com/directory type pages for studio data
    
    
    Parameters
    ----------
    
    urls: list(str)
        list of dexigner directory urls to scrape from 
    writing: bool
        are we writing these to a file today?
    studios_we_care_about: list(str)
        a list of the studio types that we care about. Ex: "Architecture Companies"
    
    Returns
    -------
    None
    """
    
    if writing:
        file = open('temp.csv', 'a+')
        writer = csv.writer(file)
        #writer.writerow(["Title", "Tele", "Email", "Web", "Addy", "Poblacion", "Type"])
    
    for url in urls:
        for i in ["", "/2", "/3"]:
            try:
                page = urlopen("https://www.dexigner.com"+url+i).read()
                soup = BeautifulSoup(page)

                for i, article in enumerate(soup.find_all('article')):
                    if i != 0:
                        if "cat" in url:
                            url_split = url.split("/") 
                            studioTypeStr = " ".join(url_split[url_split.index("cat")+1:url_split.index("loc")])
                        else:
                            studioTypeStr = article.find_all('a')[-1].contents[0]
                        
                        web = article.footer.a.contents[0]
                        if any([studioTypeStr == i for i in studios_we_care_about]):
                            # read in the new page
                            my_soup = BeautifulSoup(urlopen("https://www.dexigner.com/" + article.h3.a.get('href')).read())

                            # title
                            title = my_soup.h1.contents[0]

                            # telephone and address
                            address = my_soup.address.find_all('p')
                            try:
                                tele = address[0].a.span.contents[0]
                            except:
                                tele = "x"
                            addy = address[1].get_text().replace("Portugal", "")
                            
                            if hunter is not False:
                                email = extractEmail(web, hunter)
                            else: 
                                email = extractEmailNormal(web)
                            
                            row = [title, tele, email, web, addy, "Dexigner", studioTypeStr, ""]
                            if writing:
                                writer.writerow(row)
                                print("row written...")
                            else:
                                print(row)
                            # print(article.h3.a.contents[0])
            except HTTPError:
                continue
            
    if writing: 
        file.close()



def get_urls():
    # making list of dexigner urls that we want to scrape
    dexigner_urls = []
    base_dir = "/directory/"
    for loc in ["Spain"]:
        for page in ["loc/", "cat/Architecture/Companies/loc/"]:
            if "cat" not in page:
                for studioType in ["/Studios", "/Designers"]:
                    dexigner_urls.append(base_dir+page+loc+studioType)
            else:
                dexigner_urls.append(base_dir+page+loc)

    return dexigner_urls
