import os
import datetime
import requests
import time
import tempfile
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
load_dotenv()

import gen_intro as gen 
import search_paper as sp

CLIENT = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
CHANNELL =os.getenv("SLACK_CHANNEL") 

def post_comic(keyword, venue, year_range):


def post_daily_paper(keyword, venue, year_range):
    selected_paper = sp.research_paper(keyword, venue, year_range)
    
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

    CLIENT.chat_postMessage(
        channel=CHANNELL,
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

def post_image_url(keyword, venue, year_range):
    selected_paper = sp.research_paper(keyword, venue, year_range)
    
    image_url = gen.generate_comic(selected_paper)

    """
    指定した image_url を Slack の channel に投稿する
    """
    try:
        response = CLIENT.chat_postMessage(
            channel=CHANNELL,
            text="test",  # 画像だけ送りたいなら空文字でOK
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*どんな論文？🧐*"
                    }
                },
                {"type": "divider"},
                {
                    "type": "image",
                    "image_url": image_url,
                    "alt_text": "4コマ漫画"
                }
            ]
        )
        print(f"画像を投稿しました (ts={response['ts']})")
    except SlackApiError as e:
        print(f"Slack API エラー: {e.response['error']}")

if __name__ == "__main__":
    keyword = ' '
    venue = ('Annual IEEE International Conference on Pervasive Computing and Communications','CHI')
    year_range = 3
    # post_daily_paper(keyword, venue, year_range)
    # test_gen_comic(keyword, venue, year_range)
    # image_url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-ymJNkLG4S41rIZuoSnWOgVzi/user-FMHVKD6W1oVWCnUnsZAOYdzY/img-5MRDA8tdkTwzmFkMsOZGjvUW.png?st=2025-06-03T01%3A36%3A01Z&se=2025-06-03T03%3A36%3A01Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=475fd488-6c59-44a5-9aa9-31c4db451bea&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-06-02T19%3A49%3A19Z&ske=2025-06-03T19%3A49%3A19Z&sks=b&skv=2024-08-04&sig=cI%2BZhZYz6XCE%2By%2BlhS4u8I86dilc2qyvJL0GBMALk2E%3D"
    post_image_url(keyword, venue, year_range)
