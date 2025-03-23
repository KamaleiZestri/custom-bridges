#!/usr/bin/python3
# This script takes has one required input which is the username of a Bluesky user:
#   BlueskyRSS.py "warframe.com"
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
        <a href="https://bsky.app/profile/{username}">
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
            if isinstance(media, str) or "alt" not in media.keys():
                imageAltText = "Placeholder Text"
            else:
                imageAltText = media["alt"]
            text += f"""
            <p>{imageAltText}</p>
            """
        case "Small":
            #if put in by external, its already the raw uwl
            if isinstance(media, str):
                imageURL = media.replace(" ", "%20")
            else:
                imageURL = media["thumb"].replace(" ", "%20")
            text+= f"""
            <a href="{imageURL}">
                <img
                    style="align:top; max-width:558px; border:1px solid black;"
                    src="{imageURL}" 
                />
            </a>
            """
        case "Full":
            if isinstance(media, str):
                imageURL = media.replace(" ", "%20")
            else:
                imageURL = media["fullsize"].replace(" ", "%20")
            text+= f"""
            <a href="{imageURL}">
                <img
                    style="align:top; max-width:558px; border:1px solid black;"
                    src="{imageURL}" 
                />
            </a>
            """

    return text

def genVideoText(media):
    text = ""

    imageURL = media["thumbnail"].replace(" ", "%20")
    text+= f"""
    <p>(VIDEO POST)<p>
    <a href="{imageURL}">
        <img
            style="align:top; max-width:558px; border:1px solid black;"
            src="{imageURL}" 
        />
    </a>
    """

    if "alt" in media.keys():
        imageText=media["alt"]
        text +=  f"<p>{imageText}</p>"

    return text

def getEmbedData(embed):
    text = ""

    match embed["$type"]:
        case "app.bsky.embed.recordWithMedia#view":
            if "$type" in embed["media"]:
                text = getEmbedData(embed["media"])     
            else:
                for image in post["embed"]["media"]["images"]:
                    text += genImagesText(image)
    
        # TODO how to properly embed this...
        case "app.bsky.embed.record#view":
            text = ""

        case "app.bsky.embed.video#view":
            text += genVideoText(embed)

        case "app.bsky.embed.external#view":
            if "thumb" in embed["external"].keys():
                text += genImagesText(embed["external"]["thumb"])
            else:
                text += genImagesText(embed["external"]["uri"])

        case "app.bsky.embed.images#view":
            for image in embed["images"]:
                text += genImagesText(image)

    return text

def getItemFromPost(object:dict):
    post = object["post"]

    item:dict = {}

    item["authors"] = [{"name":post["author"]["displayName"]}]
    item["id"] = post["cid"]
    item["date_published"] = post["record"]["createdAt"]
    item["url"] = f"https://bsky.app/profile/{post["author"]["handle"]}/post/{post["uri"].split("/")[-1]}"

    if post["record"]["text"]:
        item["title"] = post["record"]["text"]
    else:
        item["title"] = f"Post by {post["author"]["displayName"]}"

  
    embeds = []

    if "embed" in post:
        embeds += getEmbedData(post["embed"]) 
    if "record" in post:
        embeds += getEmbedData(post["record"])
        
       
    if "avatar" in post["author"]:
        avatarText = genAvatarText(post["author"]["displayName"], post["author"]["avatar"], item["title"])
    else:
        avatarText = "<p>(NO AVATAR)</p>"

    embedsText = ""
    for embed in embeds:
        embedsText += embed

    item["content_html"] = f"""
    <div style="display: inline-block; vertical-align: top;">
	    {avatarText}
    </div>
    <div style="display: inline-block; vertical-align: top;">
        {post["record"]["text"]}
    </div>
    <div style="display: block; vertical-align: top;">
        {embedsText}
    </div>
    """

    return item


def getFeedDataJson(url, params, headers):
    """Run HTTP request. Repeats to get as many posts as requested."""

    #TODO why doesnt author feed give back a cursor?
    if url is BASE_URL_USER_FEED:
        if int(args.LIMIT) < 100:
            params["limit"] = args.LIMIT
        else:
             params["limit"] = "100"
        resp = requests.get(url=url, params=params, headers=headers).json()
        return resp

    fullResponse = []
    curr:int = int(args.LIMIT)
    cursor = ""

    while curr>0:
        if curr>=100:
            params["limit"] = "100"
            params["cursor"] = cursor

            resp = requests.get(url=url, params=params, headers=headers).json()

            cursor = resp["cursor"]
            curr -= 100

            fullResponse += resp["feed"]
        else:
            params["limit"] = curr

            resp = requests.get(url=url, params=params, headers=headers).json()

            curr = 0

            fullResponse += resp["feed"]
    return fullResponse



parser = argparse.ArgumentParser(description="This script outputs an RSS feed for a given Bluesky user or feed.")
parser.add_argument("username", help="Username on Bluesky")
parser.add_argument("--timeline", dest="TIMELINEPASS", default="", help="Provides app password and instructs to get user's timeline.")
parser.add_argument("--noavatar", dest="NOAVA", action="store_true", help="Will not show the user avatar in the post.")
parser.add_argument("--noreblog", dest="NOREBLOG", action="store_true", help="Do not show reblogs from the user.")
parser.add_argument("--noreply", dest="NOREPLY", action="store_true", help="Do not show replies from the user.")
parser.add_argument("--onlyimage", dest="ONLYIMAGE", action="store_true", help="Only show posts that include images.")
parser.add_argument("--image", dest="IMAGESIZE", choices=["None","Small","Full"], default="Small", help="Decide how the included image is displayed, if at all.")
parser.add_argument("--limit", dest="LIMIT", default="50", help="How many posts to get. Paginates if over 100.")
args = parser.parse_args()


BASE_URL_USER = "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile/"
BASE_URL_USER_FEED = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed/"
BASE_URL_LOGIN = "https://bsky.social/xrpc/com.atproto.server.createSession/"
BASE_URL_TIMELINE = "https://bsky.social/xrpc/app.bsky.feed.getTimeline"
feed:dict = {"items":[]}

if args.ONLYIMAGE:
    filterType = "posts_with_media"
else:
    filterType = "posts_no_replies"


if args.TIMELINEPASS !="":
    paramData = {"identifier" : args.username,
                "password" : args.TIMELINEPASS}
    loginResponse = requests.post(BASE_URL_LOGIN, json=paramData).json()
    accessKey = loginResponse["accessJwt"]
    displayName = loginResponse["handle"]

    feed["title"] = f"{displayName}'s Timeline - Bluesky"
    feed["home_page_url"] = f"https://bsky.app/profile/{args.username}"
    feed["description"] = f"Posts from the timeline {displayName} on Bluesky"

    headers = {"Authorization" : f"Bearer {accessKey}"}

    bskyJSON = getFeedDataJson(BASE_URL_TIMELINE, {}, headers)
    

else:
    profileResponse = requests.get(BASE_URL_USER, params={"actor":args.username}).json()
    displayName = profileResponse["displayName"]

    feed["title"] = f"{displayName} - Bluesky"
    feed["home_page_url"] = f"https://bsky.app/profile/{args.username}"
    feed["description"] = "Posts on Bluesky from " + displayName
    paramData = {"actor" : args.username,
                "filter" : filterType}

    bskyJSON = getFeedDataJson(BASE_URL_USER_FEED, paramData, {})
    bskyJSON = bskyJSON["feed"]


for post in bskyJSON:
    if args.NOREBLOG and (post["post"]["author"]["handle"] != args.username):
        continue

    # TODO need to improve display of replies
    # TODO maybe allow self replies?
    # TODO maybe allow certain time range replies?
    if args.NOREPLY and ("reply" in post.keys()):
        continue

    item = getItemFromPost(post)
    if item:
        feed["items"].append(item)

print(json.dumps(feed))


# TODO refactor reblogs
# 1. should show timestamp/author of reblogger (optional)
# in such a case, embed the reblog. same idea with replies
