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
                                "タイトル：<Title>\n説明：<説明文>\n出版年：<出版年>\n会議：<会議名>\n\nの形式で回答して")},
                   { "role":"user",
                     "content":f"タイトル: {paper_info['title']}\n\n要旨: {paper_info['abstract']}\n\n出版年: {paper_info['year']}\n\n会議: {paper_info['venue']}\n\n---\nこの論文のAbstractをわかりやすく説明して"}]
    )
    return chat.choices[0].message.content

if __name__ == "__main__":
    summary = summarize()
    print(summarize())