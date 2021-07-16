# tybens 14/07/2020
import argparse

from pyhunter import PyHunter
from decouple import config

from utils import extractEmail, extractEmailNormal, pickleSoups, getPickledSoups
from scrape import architizer, dexigner, archinect, zoomInfo, eArchitect


if __name__ == "__main__":
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ACTION", "-a", type=str,
                        help="str of which action to do. 'at' for 'architizer', 'an for 'archinect', 'zi' for 'zoomInfo', 'dx' for 'dexigner' and 'ea' for 'eArchitect'")
    parser.add_argument("--WRITING", "-w", type=int,
                        help="int of whether or not to write to temp.csv. 0 for False, 1 for True")
    parser.add_argument("--HUNTER", "-ht", type=int,
                        help="int of whether or not to use hunter.io to extract emails. 0 for False, 1 for True. If 0, uses a worse and slower script that I wrote to extract emails")
    args = parser.parse_args()
    action_mapper = {"at": "architizer", "an": "archinect",
                     "zi": "zoomInfo", "dx": "dexigner", "ea": "eArchitect"}
    
    # variables
    ACTION = action_mapper[args.ACTION]
    WRITING = bool(args.WRITING)
    HUNTER = False if not bool(args.HUNTER) else PyHunter(config("HUNTER_API_KEY"))

    if ACTION == "architizer":
        PROJECT = True    # search for projects done in country, not firm location
        PROJECTTYPE = "/project-type=Private House"
        COUNTRY = "Spain"  # spain
        architizer.scrape(COUNTRY, PROJECT, WRITING, HUNTER, PROJECTTYPE)

    elif ACTION == "dexigner":
        studios_we_care_about = ["Architectural Design Studios", "Interior Design Studios",
                                 "Architecture Companies", "Architecture Consultancies", "Architects", "Interior Designer"]
        urls = dexigner.get_urls()
        dexigner.scrape(urls, WRITING, studios_we_care_about, HUNTER)

    elif ACTION == "zoomInfo":
        BASE_URL = "https://www.zoominfo.com/companies-search/location-spain-industry-lodging-resorts"  # restaurants

        soups = zoomInfo.get_soups(BASE_URL)
        # pickleing logic for saving the soups we extracted
        filename = 'pickle/my_soups_hotels.pkl'  # or 'pickle/my_soups_restaurants.pkl'
        pickleSoups(soups, filename)

        zoomInfo.scrape(writing=WRITING, hunter=HUNTER, soups=soups)

    elif ACTION == "archinect":
        soups = archinect.selenium()
        archinect.scrape(WRITING, HUNTER, soups)

    elif ACTION == "eArchitect":
        eArchitect.scrape(WRITING)

    else:
        print(f"ERROR: {ACTION} action not available")
