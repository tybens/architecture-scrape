import re
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import pickle

from bs4 import BeautifulSoup
from pyhunter import PyHunter


def extractEmailNormal(url, verbose=False):
    """ This extracts emails from websites
    
    It checks the "mail-to" tag and returns the email, if none found
    we use regex to find all matching strings and return them.
    
    Parameters
    ----------
    url: str
        the url (ex: maca-archi.fr) WITHOUT https://www of the website to search for emails
        
    Returns
    -------
    str
        a string of all the emails found, or an "x" if none found
        
    
    """
    url = url.replace("https://www.", "").replace("http://www.", "").replace("http://", "").replace("https://", "")
    EMAILEXCLUDE = ["leaflet", "example.com", "vue", "axios"]
    exp = re.compile(r"(?:.*?='(.*?)')")
    exp_email = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
    for ext in ["", "/contact",  "/contact-us", "/about", "/en/contact", "/contactos", "/contacto"]:
        try:
            page = urlopen("https://"+url+ext, timeout=10).read()
        except URLError:
            try:
                page = urlopen("http://"+url+ext, timeout=10).read()
            except HTTPError:
                if verbose: print("url error, trying another")
                continue
            except:
                if verbose: print("url timed out, trying another")
                continue
        except:
            if verbose: print("url timed out, trying another")
            continue

        soup = BeautifulSoup(page)
        try:
            # Find any element with the mail icon
            for icon in soup.findAll("i", class_="icon-mail"):
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
        except:
            pass
        # uses simple regex to find emails
        emails = set(exp_email.findall(str(soup)))
        if len(emails) != 0:
            return " / ".join([x for x in filter(lambda x: any(i not in x for i in EMAILEXCLUDE), emails)])

    return "x"


def extractEmail(domain, hunter):
    """ uses hunter.io to extract emails (this is better than the above function)
    
    Parameters
    ----------
    domain : str
        string of the domain name to search in
    hunter : object
        initialized pyhunter object to do the extracting
        
    Returns
    -------
    str
        string with the format "email / email / email / ..."
    """
    
    data = hunter.domain_search(domain)
    emails = ""
    for email in data['emails']:
        emails+=email['value']+" / "
        #print(email['confidence'])
    
    if emails != "":
        emails = emails[:-3]
        
    return emails


def pickleSoups(soups, filename):
    with open(filename, 'wb') as f:
        pickle.dump([str(soup) for soup in soups], f)
        

def getPickledSoups(filename):
    with open(filename, 'rb') as f:
        str_soups = pickle.load(f)
        soups = [BeautifulSoup(str_soup, 'lxml') for str_soup in str_soups]
    return soups