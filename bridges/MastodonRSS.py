#!/usr/bin/python3

# This script takes one input which is a valid Masotodon instance and authentication token:
#   MastodonRSS.py "mastodon.social" "AUTHTOKEN"
#
# This scripts outputs JSON feed 1.1: https://jsonfeed.org/version/1.1

import argparse
import json
import sys

import requests


def genAvatarText(username, avatar, url):
    if args.NOAVA:
        return ""
    else:
        return f"""
        <a href="https://{args.instance}/@{username}">
            <img
                style="align:top; width:75px; border:1px solid black;"
                alt="{username}"
                src="{avatar}"
                title="{url}" />
            </a>
        """

def genImagesText(media):
    text = ""

    if args.IMAGESIZE == "None":
        for image in media:
            imageURL = image["url"].replace(" ", "%20")
            text += f"""
            <a href="{imageURL}">
                {imageURL}
            </a>
            """
    else:
        for image in media:
            if args.IMAGESIZE == "Small":
                imageURL = image["preview_url"].replace(" ", "%20")
            else:
                imageURL = image["url"].replace(" ", "%20")

            if image["type"] == "gifv":
                text += f"""
                <a href="{imageURL}">
                    <video autoplay muted loop
                        style="align:top; max-width:558px; border:1px solid black;"
                        src="{imageURL}" 
                    />
                </a>
                """
            else:
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
    # check for reply
    if args.NOREP and post["in_reply_to_id"] is not None:
        return []

    # check for reblog
    if post["reblog"] is None:
        embPost = False
    else:
        embPost = True

    if args.NOBOOST and embPost:
        return []

    item:dict = {}

    #incase of reblog, just get data from internal, original post
    if embPost:
        post = post["reblog"]

    item["id"] = post["id"]
    item["date_published"] = post["created_at"]
    item["url"] = post["uri"]
    item["authors"] = [post["account"]["username"]]
    if post["content"] is None:
        item["title"] = "[NO TITLE]"
    else:
        item["title"] = post["content"]

    avatarText = genAvatarText(post["account"]["username"], post["account"]["avatar"], post["account"]["url"])
    imagesText = genImagesText(post["media_attachments"])

    item["content_html"] = f"""
    <div style="display: inline-block; vertical-align: top;">
        {avatarText}
    </div>
    <div style="display: inline-block; vertical-align: top;">
        {post['content']}
    </div>
    <div style="display: block; vertical-align: top;">
        {imagesText}
    </div>
    """

    return item

parser = argparse.ArgumentParser(description ="This script outputs an RSS feed of a user's Mastodon home feed.")
parser.add_argument("instance", help="The name of the mastodon instance.")
parser.add_argument("authToken", help="User-specific app auth token.")
parser.add_argument("--noavatar", dest="NOAVA", action="store_true", help="'Hide user avatars in posts.")
parser.add_argument("--noreplies", dest="NOREP", action="store_true", help="Hide replies, as determined by relations (not mentions)")
parser.add_argument("--noboost", dest="NOBOOST", action="store_true", help="Hide boosts. This will reduce loading time the boosted status is fetched from other federated instances")
parser.add_argument("--image", dest="IMAGESIZE", choices=["None","Small","Full"], default="Full", help="Decide how the included image is displayed, if at all.")
args = parser.parse_args()

feed:dict = {"items":[]}

feed["title"] = f"Mastodon - {args.instance} Instance"
feed["home_page_url"] = f"https://www.{args.instance}/"
feed["description"] = f"Read your mastodon feed from {args.instance}"


url = f"https://{args.instance}/api/v1/timelines/home";
headers = {"Authorization" : f"Bearer {args.authToken}"}

mastodonJSON = requests.get(url, headers=headers).json()

for post in mastodonJSON:
    item = getItemFromPost(post)
    if item:
        feed["items"].append(item)

print(json.dumps(feed))
