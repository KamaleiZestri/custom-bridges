#!/usr/bin/python3

# This script takes one input which is the username of a Pillowfort user such as:
#   PillowfortRSS.py "Staff"
#
# This scripts outputs JSON feed 1.1: https://jsonfeed.org/version/1.1

import argparse
import json

import requests


def genAvatarText(username, avatar, url):
    if args.NOAVA:
        return ""
    else:
        return f"""
        <a href={BASEURL}/posts/{username}">
            <img
                style="align:top; width:75px; border:1px solid black;"
                alt="{username}"
                src="{avatar}"
                title="{url}" />
            </a>
        """

def genImagesText(media):
    text = ""

    match args.IMAGESIZE:
        case "None":
            for image in media:
                imageURL = image["url"].replace(" ", "%20")
                text += f"""
                <a href="{imageURL}">
                    {imageURL}
                </a>
                """
        case "Small":
            for image in media:
                imageURL = image["small_image_url"].replace(" ", "%20")
                text+= f"""
                <a href="{imageURL}">
                    <img
                        style="align:top; max-width:558px; border:1px solid black;"
                        src="{imageURL}" 
                    />
                </a>
                """
        case "Full":
             for image in media:
                imageURL = image["url"].replace(" ", "%20")
                text+= f"""
                <a href="{imageURL}">
                    <img
                        style="align:top; max-width:558px; border:1px solid black;"
                        src="{imageURL}" 
                    />
                </a>
                """

    return text

def getItemFromPost(post:dict):
     # check for reblog
    if post["original_post_id"] is None:
        embPost = False
    else:
        embPost = True

    if args.NOREBLOG and embPost:
        return {}

    item:dict = {}

    item["id"] = post["id"]
    item["date_published"] = post["created_at"]
    if embPost:
        item["url"] = F"{BASEURL}/posts/{post["original_post"]["id"]}"
        item["authors"] = [{"name":post["original_username"]}]
        if post["original_post"]["title"] != "":
            item["title"] = post["original_post"]["title"]
        else:
            item["title"] = "[NO TITLE]"
    else:
        item["url"] = F"{BASEURL}/posts/{post["id"]}"
        item["authors"] = [{"name":post["username"]}]
        if post["title"] != "":
            item["title"] = post["title"]
        else:
            item["title"] = "[NO TITLE]"

    # Four cases if it is a reblog.
    #  1: reblog has tags, original has tags. defer to option.
    #  2: reblog has tags, original has no tags. use reblog tags.
    #  3: reblog has no tags, original has tags. use original tags.
    #  4: reblog has no tags, original has no tags. use reblog tags not that it matters.
    item["tags"] = post["tags"]
    if embPost:
        if args.NORETAGS or post["tags"] is None:
            item["tags"] = post["original_post"]["tag_list"]

    avatarText = genAvatarText(post["username"], post["avatar_url"], item["title"])
    imagesText= genImagesText(post["media"])

    item["content_html"] = f"""
    <div style="display: inline-block; vertical-align: top;">
	    {avatarText}
    </div>
    <div style="display: inline-block; vertical-align: top;">
        {post["content"]}
    </div>
    <div style="display: block; vertical-align: top;">
        {imagesText}
    </div>
    """

    return item


parser = argparse.ArgumentParser(description = "This script outputs an RSS feed of posts for the given Pillowfort user.")
parser.add_argument("username", help="Username of a Pillowfort user.")
parser.add_argument("--noavatar", dest="NOAVA", action="store_true", help="Will not show the user avatar in the post.")
parser.add_argument("--noreblog", dest="NOREBLOG", action="store_true", help="Will only show original posts from the user.")
parser.add_argument("--noretags", dest="NORETAGS", action="store_true", help="Will use tags from the original post(if avaialable) instead of the reblog.")
parser.add_argument("--image", dest="IMAGESIZE", choices=["None","Small","Full"], default="Full", help="Decide how the included image is displayed, if at all.")
args = parser.parse_args()

BASEURL = "https://www.pillowfort.social"
feed:dict = {"items":[]}

feed["title"] = f"{args.username} - Pillowfort"
feed["home_page_url"] = f"https://www.pillowfort.social/{args.username}/json/?p=1"
feed["description"] = f"Get the latest posts from {args.username} on Pillowfort."

pillowfortJSON = requests.get(feed["home_page_url"]).json()

for post in pillowfortJSON["posts"]:
    item = getItemFromPost(post)
    if item:
        feed["items"].append(item)

print(json.dumps(feed))
