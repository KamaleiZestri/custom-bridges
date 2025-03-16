#!/usr/bin/python3

# This script expects one input which is your Baka Updates list such as:
#   BakaRSS.py "ReadingList.json"
# Follow these steps to get the JSON file or use the BakaRSS Lister Userscript:
# 1. Go to any Baka Updates List page. ex; Reading List
# 2. Right click -> "Developer Tools" -> "View Page Source"
# 3. On the new page, copy and paste all the contents into a new file of your own called `input.html`.
# 4. Run "BakaRSS.py --import input.html"
# 5. Rename the result `output.html`
# This scripts outputs JSON feed 1.1: https://jsonfeed.org/version/1.1

import argparse
import json
import re
import urllib.request

from bs4 import BeautifulSoup


def findID(tag):
    result = re.findall(r"/series/([0-9a-zA-Z]*)/", tag.get("href"))
    if len(result) > 0:
        return result[0]
    else:
        return 0
    

def importable(rawFile):
    with open(rawFile) as file:
        listComp = {}
        listHTML = file.read()
        listSoup = BeautifulSoup(listHTML, "html.parser")
        listData = listSoup.select(".series-list-table_list_table__H2pQ5 > [class='row g-0']")

        for entry in listData:
            id = findID(entry.select("a")[0])
            title = entry.select("a")[0].getText()
            listComp[id] = title

        with open("output.json", "w") as outfile:
            json.dump(listComp, outfile)



parser = argparse.ArgumentParser(description="This script outputs a filtered Releases feed from BakaUpdates")
parser.add_argument("file", help="Selected file.")
parser.add_argument("--import", dest="IMPORTABLE", action="store_true", help="Treat the file as a list to be converted to json.")

args = parser.parse_args()

if (args.IMPORTABLE):
    importable(args.file)
    exit()


RELEASES_URL:str = "https://www.mangaupdates.com/releases.html"


feed:dict = {"items":[]}

feed["title"] = "Baka Updates Manga Releases"
feed["home_page_url"] = "https://www.mangaupdates.com/"
feed["description"] = "Get the latest series releases from your follows list"


#get all manga on releases page; usually about 3 days back
releasesHTML:str = urllib.request.urlopen(RELEASES_URL)
releasesSoup = BeautifulSoup(releasesHTML, "html.parser")
releasesList = releasesSoup.select("[class='col-12 row g-0 new-release-item_alt__jZKeE']")



#load file with ids to a list
with open(args.file) as file:
    idList = list(json.load(file).keys())


#search each item in bakaupdates to see if in idlist
for manga in releasesList:
    id = findID(manga.select("a")[0])
    if not id in idList: continue

    item = {}
    item["content_html"] = ""

    objTitle = manga.select("a")[0]
    if objTitle:
        title = objTitle.getText()
        # If it ends in a star, remove the ending star.
        if title[-1] == "*":
            title = title[:-1]
        item["content_html"] += "<p>Series: {0} </p>".format(str(objTitle))
    
    objVolChap = manga.select("div")[1]
    if objVolChap and objVolChap.getText() != "":
        title += objVolChap.getText()

    objAuthor = manga.select("a")[1]
    if objAuthor:
        item["authors"] = [{"name":objAuthor.getText()}]
        item["content_html"] += "<p>Groups: {0} </p>".format(str(objAuthor))

    item["title"] = title
    item["url"] = "https://www.mangaupdates.com/series/{0}".format(id)
    item["id"] = hash(id + objVolChap.getText() + objAuthor.getText())

    feed["items"].append(item)

print(json.dumps(feed))
