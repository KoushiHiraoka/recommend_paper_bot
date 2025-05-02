import os, json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def summarize(paper_info):
    client = OpenAI()
    chat = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{ "role":"system",
                    "content": ("あなたは分野初心者をアシスタントするフレンドリーな先生です"
                               "以下の形式でSlack向けにMarkdown装飾を使って出力してください。\n\n"
                                "*今日のおすすめ論文*\n"
                                "*タイトル*：<タイトル>\n"
                                "*概要*：<説明>\n"
                                "*出版年*：<出版年>\n"
                                "*会議*：<会議名>\n"
                                "*URL*：<URL>\n\n"
                                "上のテンプレートを使い、最後に要旨を簡潔かつ親しみやすい口調でまとめてください。"
            )},
                   { "role":"user",
                     "content":f"タイトル: {paper_info['title']}\n\n要旨: {paper_info['abstract']}\n\n出版年: {paper_info['year']}\n\n会議: {paper_info['venue']}\n\n会議: {paper_info['url']}\n\n---\nこの論文のAbstractをわかりやすくフレンドリーな感じで説明して"}]
    )
    return chat.choices[0].message.content

if __name__ == "__main__":
    summary = summarize()
    print(summarize())