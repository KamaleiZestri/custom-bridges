#!/usr/bin/python3

# This script is made to run off 3 required inputs which are: 
# 1. Refresh Token
# 2. Client ID
# 3. Client Secret
# 
#   MDexRSS.py clid clis --refresh reftok
#
# Also has the option to get the refresh token using username and pass.
#
#   MDexRSS.py clid clis --username user --password pass
# 
# To view how to get Client ID and Client secret, go to 
# https://api.mangadex.org/docs/02-authentication/personal-clients/
#
# This scripts outputs JSON feed 1.1: https://jsonfeed.org/version/1.1

import argparse
import json

import requests


def getItemFromPost(post:dict):
    item = {}

    manga:dict = {}
    group:dict = {}
    # Get manga and translation group relations, if present
    for relation in post["relationships"]:
        if relation["type"] == "manga":
            manga = relation
        if relation["type"] == "scanlation_group":
            group = relation


    item["id"] = post["id"]
    item["date_published"] = post["attributes"]["publishAt"]
    item["url"] = f"https://mangadex.org/chapter/{item["id"]}"

    if group:
        item["authors"] = [{"name":group["attributes"]["name"]}]
        contentGroup = f'<p>Group: <a href="{group["attributes"]["website"]}"></a>{group["attributes"]["name"]}</p>'
    else:
        item["authors"] = [{"name": "Original"}]
        contentGroup = f'<p>Group: Original</p>'

    if args.LANG in manga["attributes"]["title"]:
        item["title"] = manga["attributes"]["title"][args.LANG]
        contentSeries = f'<p>Series: <a href="https://mangadex.org/title/{manga["id"]}">{manga["attributes"]["title"][args.LANG]}</a></p>'
    else:
        altLang = next(iter(manga["attributes"]["title"]))
        item["title"] = manga["attributes"]["title"][altLang]
        contentSeries = f'<p>Series: <a href="https://mangadex.org/title/{manga["id"]}">{item["title"]}</a></p>'

    if post["attributes"]["volume"] != "None":
        item["title"] += f" V. {post["attributes"]["volume"]}"

    item["title"] += f" C. {post["attributes"]["chapter"]}"


    item["content_html"] = contentSeries + contentGroup
    item["content_html"] += f"<p>New {post["attributes"]["pages"]} page chapter.</p>"

    return item


def getRefreshToken(username:str, password:str, clientid:str, clientpass:str):
    creds = {
        "grant_type": "password",
        "username": args.username,
        "password": args.password,
        "client_id": args.clientid,
        "client_secret": args.clientsecret
    }
    r = requests.post(
            "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token",
            data=creds
    )

    refreshToken = r.json()["refresh_token"]
    return refreshToken

def getAccessToken(refreshToken:str, clientid:str, clientsecret:str):
    creds = {
        "grant_type": "refresh_token",
        "refresh_token": refreshToken,
        "client_id": clientid,
        "client_secret": clientsecret
    }

    r = requests.post("https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token",data=creds)
    accessToken = r.json()["access_token"]
    return accessToken


parser = argparse.ArgumentParser(description ="This script outputs an RSS feed of a user's Mangadex follows feed.")
parser.add_argument("clientid", help="The user's Mangadex client id.")
parser.add_argument("clientsecret", help="The user's Mangadex client secret.")
parser.add_argument("--username", help="The user's Mangadex username.")
parser.add_argument("--password", help="The user's Mangadex password.")
parser.add_argument("--refresh", help="The user's Mangadex refresh token.")
parser.add_argument("--lang", dest="LANG", default="en", help="The language of chapter updates to get. Defualts to English (en)")
args = parser.parse_args()

feed:dict = {"items":[]}

feed["title"] = "Mangadex Follows Feed"
feed["home_page_url"] = "https://mangadex.org/titles/feed"
feed["description"] = "Read your Mangadex Follows feed."


if args.username and args.password:
    token = getRefreshToken(args.username, args.password, args.clientid, args.clientsecret)
    print(f"Refresh Token:\n{token}")
    quit()
elif args.refresh:
    accessToken = getAccessToken(args.refresh, args.clientid, args.clientsecret)
else:
    print("Either '--refresh' or '--user' and '--pass' need to be provided!")
    quit()

# Get feed
headers = {"Authorization" : f"Bearer {accessToken}"}
params = {}
params["order[publishAt]"] = "desc"
params["limit"] = 100
params["translatedLanguage[]"] = [args.LANG]
params["includes[]"] = {"manga", "scanlation_group"}
mdexJSON = requests.get("https://api.mangadex.org/user/follows/manga/feed", params=params, headers=headers).json()


for post in mdexJSON["data"]:
    item = getItemFromPost(post)
    if item:
        feed["items"].append(item)

print(json.dumps(feed))
