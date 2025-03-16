#!/usr/bin/python3

# This script takes one input which is the username of a Newgrounds user such as:
#   NewgroundsRSS.py "TomFulp"
#
# This scripts outputs JSON feed 1.1: https://jsonfeed.org/version/1.1

import json
import sys
import urllib.request

from bs4 import BeautifulSoup

username = sys.argv[1]

feed:dict = {"items":[]}


feed["title"] = f"{username} - Newgrounds"
feed["home_page_url"] = f"https://{username}.newgrounds.com/"
feed["description"] = f"Get the latest art from {username} on Newgrounds."

artHTML:str = urllib.request.urlopen(f"https://{username}.newgrounds.com/art")
artSoup = BeautifulSoup(artHTML, "html.parser")
artData = artSoup.select(".item-portalitem-art-medium")


for post in artData:
    item = {}

    item["authors"] = [{"name":username, "url":feed["home_page_url"]}]
    # artist = {}
    # artist["name"] = username
    # item["authors"].append(artist)
    #TODO could add "url" and "avatar" but needs a little more work for it
    item["url"] = post.get("href")

    titleOrRestricted = post.select_one("h4").get_text()

    if titleOrRestricted == "Restricted Content: Sign in to view!":
        item["title"] = f"NSFW: {item['url']}"
        item["content_html"] = f'<a href="{item["url"]}">{item["title"]}</a>'
    else:
        item["title"] = titleOrRestricted
        item["content_html"] = f"""
        <a href="{item['url']}">
        <img
            style="align:top; width:270px; border:1px solid black;"
            alt="{item['title']}"
            src="{post.select_one("img").get("src")}"
            title="{item['title']}" />
        </a>
        """
    feed["items"].append(item)

print(json.dumps(feed))
