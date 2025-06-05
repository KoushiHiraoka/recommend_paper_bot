import os, io
import datetime
import requests
import time
import tempfile
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

import gen_intro as gen 
import search_paper as sp

CLIENT = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
CHANNEL =os.getenv("SLACK_CHANNEL") 

def post_daily_paper(keyword, venue, year_range):
    selected_paper = sp.research_paper(keyword, venue, year_range)
    print(selected_paper)
    gpt_summary = gen.summarize(selected_paper)
    pop_title = gen.gen_title(selected_paper)

    title    = selected_paper.get("title")
    year     = selected_paper.get("year")
    venue    = selected_paper.get("venue")
    url      = selected_paper.get("url")
    authors  = ", ".join(a["name"] for a in selected_paper.get("authors", []))
    citation = selected_paper.get("citationCount")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": pop_title,
                "emoji": True
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text":
                    f"*✏️ タイトル*\n<{url}|{title}>\n"
                    f"*📅 出版年*\n{year}\n"
                    f"*🏷️ 会議*\n{venue}\n"
                    f"*📈 引用数*\n{citation}\n"
                    f"*👤 著者*\n{authors}"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*どんな論文？🧐*\n{gpt_summary}", 
            }
        }
    ]

    CLIENT.chat_postMessage(
        channel=CHANNEL,
        blocks=blocks,
        text="今日のおすすめ論文をお届けします"  # フォールバックテキスト
    )
    # text = (
    #     f"{gpt_summary}"
    # )
    # client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    # try:
    #     client.chat_postMessage(
    #         channel=os.getenv("SLACK_CHANNEL"),
    #         text=text
    #     )
    #     print("Posted to Slack successfully.")
    # except SlackApiError as err:
    #     print("Failed to post to Slack:", err)



if __name__ == "__main__":
    keyword = ' '
    venue = ('Annual IEEE International Conference on Pervasive Computing and Communications','CHI')
    year_range = 3
    post_daily_paper(keyword, venue, year_range)

