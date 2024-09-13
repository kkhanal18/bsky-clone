#!/usr/bin/env python3

"""
Script demonstrating how to create posts using the Bluesky API, covering most of the features and embed options.

To run this Python script, you need the 'requests' and 'bs4' (BeautifulSoup) packages installed.
"""

import re
import os
import sys
import json
import argparse
from typing import Dict, List
from datetime import datetime, timezone
import time


import requests
from bs4 import BeautifulSoup


def bsky_login_session(pds_url: str, handle: str, password: str) -> Dict:
    resp = requests.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    return resp.json()


def create_post(text):
    print('inside')
    session = bsky_login_session('https://bsky.social', 'foggybear196@gmail.com', 'ehn1xjw*reu4DKQ1fuq')

    # these are the required fields which every post must include
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    post = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now
    }


    print("creating post:", file=sys.stderr)
    print(json.dumps(post, indent=2), file=sys.stderr)

    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + session["accessJwt"]},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )
    print("createRecord response:", file=sys.stderr)
    print(json.dumps(resp.json(), indent=2))
    resp.raise_for_status()

def fetch_polls():
    url = 'https://projects.fivethirtyeight.com/polls/president-general/2024/national/polls.json'
    response = requests.get(url)
    if response.status_code == 200:
        polls_data = response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
    with open('data.json', 'w') as f:
        json.dump(polls_data, f)
    return polls_data

def check_polls(fetched_data):
    new_polls = []
    try:
        with open('poll_ids.json', 'r') as file:
            try:
                poll_ids = json.load(file)
            except json.JSONDecodeError:
                poll_ids = []
    except FileNotFoundError:
            poll_ids = []
    for poll in fetched_data:
        id = poll['id']
        if id not in poll_ids:
            new_polls.append(poll)
            poll_ids.append(id) 
            with open('poll_ids.json', 'w') as file:
                json.dump(poll_ids, file, indent=4)

    pollster = fetched_data[0]["pollster"]
    first_choice = fetched_data[0]["answers"][0]["choice"]
    first_pct = fetched_data[0]["answers"][0]["pct"]
    second_choice = fetched_data[0]["answers"][1]["choice"]
    second_pct = fetched_data[0]["answers"][1]["pct"]
    sample_size = fetched_data[0]["sampleSize"]
    population = fetched_data[0]["population"]
    end_date = fetched_data[0]["endDate"]
    url = fetched_data[0]["url"]

    poll_info = (
    f"New poll from {pollster}\n"
    f"\n"
    f"{first_choice}: {first_pct}%\n"
    f"{second_choice}: {second_pct}%\n"
    f"\n"
    f"{sample_size}{population} {end_date}"
    f"\n"
    f"{url}"
    )

    return fetched_data[0]

def main():

    polls = fetch_polls()
    new_polls = [check_polls(polls)]

    if len(new_polls) < 20:
        for poll in new_polls:
            print(poll)
            pollster = poll["pollster"]
            first_choice = poll["answers"][0]["choice"]
            first_pct = poll["answers"][0]["pct"]
            second_choice = poll["answers"][1]["choice"]
            second_pct = poll["answers"][1]["pct"]
            sample_size = poll["sampleSize"]
            population = poll["population"]
            end_date = poll["endDate"]
            url = poll["url"]

            text = (
            f"New poll from {pollster}\n"
            f"\n"
            f"{first_choice}: {first_pct}%\n"
            f"{second_choice}: {second_pct}%\n"
            f"\n"
            f"{sample_size}{population} {end_date}"
            f"\n"
            f"{url}"
            )
            
            create_post(text)
    


if __name__ == "__main__":
    main()
