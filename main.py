import requests
from dotenv import load_dotenv
import os

load_dotenv()

base_url = "https://api.mangadex.org"
title = os.getenv("TITLE")

r = requests.get(f"{base_url}/manga", params={"title": title})

# get manga id
manga_id = r.json()["data"][0]["id"]

r = requests.get(
    f"{base_url}/manga/{manga_id}/feed",
    params={"order[chapter]": "desc", "translatedLanguage[]": "en"},
)

# get chapter id, number, title
chapter = r.json()["data"][0]
chapter_id = chapter["id"]
chapter_num = chapter["attributes"]["chapter"]
chapter_title = chapter["attributes"]["title"]
