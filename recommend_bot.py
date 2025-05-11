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

# def get_summary(keyword, venue):
#     selected_paper = sp.research_paper(keyword, venue)
#     return gen.summarize(selected_paper)

def post_daily_paper(keyword, venue):
    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    channel=os.getenv("SLACK_CHANNEL")

    selected_paper = sp.research_paper(keyword, venue)
    
    gpt_summary = gen.summarize(selected_paper)
    pop_title = gen.gen_title(selected_paper)

    title    = selected_paper.get("title")
    year     = selected_paper.get("year")
    venue    = selected_paper.get("venue")
    url      = selected_paper.get("url")
    authors  = ", ".join(a["name"] for a in selected_paper.get("authors", []))
    citation = selected_paper.get("citationCount")

    ## v1 blocks 
    # blocks = [
    #     {"type":"header",
    #      "text":{"type":"plain_text","text":"📚 今日のおすすめ論文 📚","emoji":True}},
    #     {"type":"section",
    #      "fields":[
    #          {"type":"mrkdwn","text":f"*タイトル*\n<{url}|{title}>"},
    #          {"type":"mrkdwn","text":f"*出版年*\n{year}"},
    #          {"type":"mrkdwn","text":f"*会議*\n{venue}"},
    #          {"type":"mrkdwn","text":f"*引用数*\n{citation}"},
    #          {"type":"mrkdwn","text":f"*著者*\n{authors}"}
    #      ]},
        # {"type":"divider"},
        # {"type":"section",
        #  "text":{"type":"mrkdwn","text":f"*要旨*\n{summary_text}"}}
    # ]

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{pop_title}",
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

    client.chat_postMessage(
        channel=channel,
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
    # venue = ('IEEE International Conference on Pervasive Computing and Communications','CHI')
    venue = 'CHI'
    # selected_paper = sp.research_paper(keyword, venue)
    # summary = gen.summarize(selected_paper)
    # print(summary)
    post_daily_paper(keyword, venue)
