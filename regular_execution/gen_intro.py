import os, json, base64
from openai import OpenAI
from dotenv import load_dotenv

import search_paper as sp

load_dotenv()
OPENAI   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_comic(paper_info):
    prompt= ("Create a 4-panel comic in English based on the following academic paper.\n\n"
    f"Title: {paper_info['title']}\n"
    f"Abstract: {paper_info['abstract']}\n\n"
    "Each panel should be a simple cartoon-style illustration, "
    "with an Japanese speech bubble (approximately 20–30 words max) appropriate for each scene.")

    # プロンプトやサイズ、背景透明指定など
    response = OPENAI.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality = 'high'
    )

    # 返ってきたデータから Base64 文字列を取り出す
    image_base64 = response.data[0].b64_json

    # Base64 → バイナリに変換
    image_bytes = base64.b64decode(image_base64)

    # ファイルに書き込み
    # output_path = "sprite.png"
    # with open(output_path, "wb") as f:
    #     f.write(image_bytes)

    # print(f"画像ファイルを保存しました: {output_path}")

    return image_bytes



def generate_sprite_sheet():
    """
    gpt-image-1 モデルで 2D ピクセルアート風のネコのスプライトシートを生成し、
    ローカルに 'sprite.png' として保存します。
    """
    # プロンプトやサイズ、背景透明指定など
    response = OPENAI.images.generate(
        model="gpt-image-1",
        prompt="Draw a 2D pixel art style sprite sheet of a tabby gray cat",
        size="1024x1024",
        quality = 'high'
    )

    # 返ってきたデータから Base64 文字列を取り出す
    image_base64 = response.data[0].b64_json

    # Base64 → バイナリに変換
    image_bytes = base64.b64decode(image_base64)

    # ファイルに書き込み
    output_path = "sprite.png"
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"画像ファイルを保存しました: {output_path}")

def summarize(paper_info):
    chat = OPENAI.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{ "role":"system",
                    # "content": ("あなたは分野初心者をアシスタントするフレンドリーな先生です"
                    #            "以下の形式でSlack向けにMarkdown装飾を使って出力してください。\n\n"
                    #             "*今日のおすすめ論文*\n"
                    #             "*タイトル*：<タイトル>\n"
                    #             "*概要*：<説明>\n"
                    #             "*出版年*：<出版年>\n"
                    #             "*会議*：<会議名>\n"
                    #             "*URL*：<URL>\n\n"
                    #             "上のテンプレートを使い、最後に要旨を簡潔かつ親しみやすい口調でまとめてください。"
                    "content":("あなたは分野初心者をサポートするフレンドリーな先生です。"
                    "これから渡す論文のタイトル、要旨、出版年、会議、URLを読み取り、"
                    "要旨をSlackのBlock Kitで使いやすいように「本文テキストだけ」を"
                    "親しみやすい口調で短くまとめてください。"
            )},
                   { "role":"user",
                     "content":f"タイトル: {paper_info['title']}\n\n要旨: {paper_info['abstract']}\n\n出版年: {paper_info['year']}\n\n会議: {paper_info['venue']}\n\n会議: {paper_info['url']}\n\n---\nこの論文のAbstractをわかりやすくフレンドリーな感じで説明して"}]
    )
    return chat.choices[0].message.content

def gen_title(paper_info):
    chat = OPENAI.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{ "role":"system",
                    # "content": ("あなたは分野初心者をアシスタントするフレンドリーな先生です"
                    #            "以下の形式でSlack向けにMarkdown装飾を使って出力してください。\n\n"
                    #             "*今日のおすすめ論文*\n"
                    #             "*タイトル*：<タイトル>\n"
                    #             "*概要*：<説明>\n"
                    #             "*出版年*：<出版年>\n"
                    #             "*会議*：<会議名>\n"
                    #             "*URL*：<URL>\n\n"
                    #             "上のテンプレートを使い、最後に要旨を簡潔かつ親しみやすい口調でまとめてください。"
                    "content":("あなたは分野初心者をサポートするフレンドリーな先生です。"
                    "これから渡す論文のタイトル、要旨を読み取り、"
                    "要旨をSlackのBlock Kitで使いやすいように「タイトルだけ」を"
                    "コピーライティングを意識してキャッチーなタイトルをつけてください。"
            )},
                   { "role":"user",
                     "content":f"タイトル: {paper_info['title']}\n\n要旨: {paper_info['abstract']}\n\n---\nコピーライティングを意識してキャッチーなタイトルをつけてください。"}]
    )
    return chat.choices[0].message.content

if __name__ == "__main__":
    # summary = summarize()
    # print(summarize())
    selected_paper = sp.research_paper(keyword=" ", venues=('CHI',), year_range=3)
    generate_comic(selected_paper)