#!/usr/bin/python3

# This script takes one input which is the searchable tags:
#   GelbooruRSS.py "mega_man_(series)"
#
# This scripts outputs JSON feed 1.1: https://jsonfeed.org/version/1.1

import argparse
import json
import urllib.parse as urlencode

import requests

parser = argparse.ArgumentParser(description ="This script outputs an RSS feed of Gelbooru's search tags.")
parser.add_argument("search", help="Tags to search for")
parser.add_argument("--page", dest="page", default="0", help="'What page of the search to stare pulling from.'")
parser.add_argument("--limit", dest="limit", default="100", help="'How many posts to pull. Max of 1000'")
args = parser.parse_args()

feed:dict = {"items":[]}

feed["title"] = f"Gelbooru - {args.search}"
feed["home_page_url"] = f"https://gelbooru.com/index.php?page=post&s=list&tags={urlencode.quote(args.search)}"
feed["description"] = f"Read Gelbooru search for the following tags: {args.search} "

searchURL = (f"https://gelbooru.com/index.php?&page=dapi&s=post&q=index&json=1&"
                f"pid={args.page}&limit={args.limit}&tags={urlencode.quote(args.search)}")
booruJSON = requests.get(searchURL).json()

#Gelooru does not put their content in the root.
if (type(booruJSON) is dict):
    booruJSON = booruJSON["post"]

for post in booruJSON:
    item = {}

    item["id"] = post["id"]
    item["date_published"] = post["created_at"]
    item["url"] = f"https://gelbooru.com/index.php?page=post&s=view&id={item["id"]}"
    item["title"] = f"Gelbooru | {item["id"]}"

    item["content_html"] = f"""
        <a href="{item["url"]}"><img src="{post["preview_url"]}"></a>
        <br><br>
        <b>Dimensions:</b> {post["width"]} x {post["height"]}
        <br><br>
        <b>Tags:</b> {post["tags"]}
        <br><br>
        <b>Source:</b><a href="{post["source"]}"> {post["source"]}</a>
        """

    feed["items"].append(item)

print(json.dumps(feed))
