import os
import datetime
import requests
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
load_dotenv()

import gen_intro as gen 
import search_paper as sp

def get_summary(keyword, venue):
    selected_paper = sp.research_paper(keyword, venue)
    return gen.summarize(selected_paper)

def post_daily_paper(keyword, venue):
    gpt_summary = get_summary(keyword, venue)
    text = (
        f"{gpt_summary}"
    )
    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    try:
        client.chat_postMessage(
            channel=os.getenv("SLACK_CHANNEL"),
            text=text
        )
        print("Posted to Slack successfully.")
    except SlackApiError as err:
        print("Failed to post to Slack:", err)

if __name__ == "__main__":
    keyword = "Human activity recognition"
    venue = ('IEEE International Conference on Pervasive Computing and Communications',)
    # selected_paper = sp.research_paper(keyword, venue)
    # summary = gen.summarize(selected_paper)
    # print(summary)
    post_daily_paper(keyword, venue)
