#!/usr/bin/python3

# This script expects one input which is your Baka Updates list such as:
#   BakaRSS.py "ReadingList.html"
# Follow these steps to get the HTML file:
# 1. Go to any Baka Updates List page. ex; Reading List
# 2. Right click -> "Developer Tools" -> "Inspect"
# 3. On the new page, copy and paste all the contents into a new HTML file of your own.
# This scripts outputs JSON feed 1.1: https://jsonfeed.org/version/1.1

import json
import re
import sys
import urllib.request

from bs4 import BeautifulSoup


def findID(tag):
    if tag.find("a") != None:
        return re.findall(r"/series/([0-9a-zA-Z]*)/", tag.find("a").get("href"))[0]
    else:
        return 0

RELEASES_URL:str = "https://www.mangaupdates.com/releases.html"


feed:dict = {"items":[]}

feed["title"] = "Baka Updates Manga Releases"
feed["home_page_url"] = "https://www.mangaupdates.com/"
feed["description"] = "Get the latest series releases from your follows list"


#get all manga on releases page; usually about 3 days back
releasesHTML:str = urllib.request.urlopen(RELEASES_URL)
releasesSoup = BeautifulSoup(releasesHTML, "html.parser")
releasesData = releasesSoup.select("div#main_content div.row > div.pbreak")

releasesList = []
for i in range(0,len(releasesData),3):
    releasesList.append([releasesData[i], releasesData[i+1], releasesData[i+2]])


#parse html file for list of following manga IDs
with open(sys.argv[1]) as file:
# with open("holdem.html") as file:
    listHTML = file.read()
listSoup = BeautifulSoup(listHTML, "html.parser")
listData = listSoup.select("table#ptable tr > td.pl")

idList = []
for mangaData in listData:
    idList.append(findID(mangaData))

#search each item in bakaupdates to see if in idlist
for manga in releasesList:
    id = findID(manga[0])
    if not id in idList: continue

    item = {}
    item["content_html"] = ""

    objTitle = manga[0]
    if objTitle:
        title = objTitle.getText()
        # If it ends in a star, remove the ending star.
        if title[-1] == "*":
            title = title[:-1]
        item["content_html"] += "<p>Series: {0} </p>".format(str(objTitle))
    
    objVolChap = manga[1]
    if objVolChap and objVolChap.getText() != "":
        title += objVolChap.getText()

    objAuthor = manga[2]
    if objAuthor:
        item["authors"] = [{"name":objAuthor.getText()}]
        item["content_html"] += "<p>Groups: {0} </p>".format(str(objAuthor))

    item["title"] = title
    item["url"] = "https://www.mangaupdates.com/series/{0}".format(id)
    item["id"] = hash(id + objVolChap.getText() + objAuthor.getText())

    feed["items"].append(item)

print(json.dumps(feed))
