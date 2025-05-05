from slack_sdk import WebClient
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

S2_KEY   = os.getenv("S2_API_KEY")
OPENAI   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SLACK    = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))