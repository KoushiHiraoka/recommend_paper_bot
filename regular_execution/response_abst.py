import os
import io
import logging
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk.errors import SlackApiError
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN    = os.getenv("SLACK_BOT_TOKEN")      
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")  
CHANNEL            = os.getenv("SLACK_CHANNEL")              
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]  = './service_account_key.json'

# Firestore クライアント初期化
db = firestore.Client()
posts_collection = db.collection(CHANNEL)

# ----------------------------
# 2. Slack Bolt アプリ初期化
# ----------------------------
bolt_app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)
handler = SlackRequestHandler(bolt_app)

flask_app = Flask(__name__)

@flask_app.route("/slack/events", methods=['POST'])
def webhook():                     
    return handler.handle(request)


@bolt_app.event("message")
def handle_message_events(event, say):
    # (1) Bot 自身のメッセージには反応しない
    if event.get("bot_id"):
        return

    text = event.get("text", "").strip().lower()
    # (2) スレッド返信であれば、thread_ts というキーが入ってくる
    #     Slack のイベントペイロードでは “thread_ts” がルートメッセージの ts になる
    thread_ts = event.get("thread_ts")  
    # ts = event.get("ts")
    # if thread_ts is None or thread_ts == ts:
    #     return

    if thread_ts and "アブスト" in text:
        # Firestore からドキュメントを読み込む
        doc_ref = posts_collection.document(thread_ts)
        doc_snapshot = doc_ref.get()

        if not doc_snapshot.exists:
            say(
                text="すみません、このスレッドの abstract は見つかりませんでした。",
                thread_ts=thread_ts
            )
            return

        data = doc_snapshot.to_dict()
        abstract = data.get("abstract", "")
        if not abstract:
            say(
                text="abstract の内容が空です。",
                thread_ts=thread_ts
            )
            return

        # (4) 見つかった abstract をスレッドに返信
        say(
            text=f"*Abstract:*\n{abstract}",
            thread_ts=thread_ts
        )


def forward():
    from pyngrok import ngrok
    authtoken = os.getenv('NGROK_AUTHTOKEN')
    if authtoken:
        ngrok.set_auth_token(authtoken)

    tunnel = ngrok.connect(8088, 'http') 
    print('Public URL:', tunnel.public_url) 

if __name__ == "__main__":
    if os.getenv('ENV') == 'dev':   # ローカル開発だけトンネル
        forward()

    flask_app.run(host='0.0.0.0', port=8088) 