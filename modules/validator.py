from actions import check_if_pdf, check_if_fullinfo, get_html
from selenium import webdriver
from selenium.webdriver.common.by import By
from openai import OpenAI
from config import Config
from session_manager import start_session
import json
import time
import os
from dotenv import load_dotenv
import rich
from prompts.coding_prompts import role_message, user_message
from rich.console import Console

console = Console()
PDF_PROMPTS = json.load(open(Config.PDF_PROMPT_PATH, "r"))
MODEL = Config.MODEL_NAME
load_dotenv()
API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=API_KEY)

def validate(selenium_session: webdriver,
             some_url: str,
             sleep_time: int=5) -> dict:
    """
    Returns dict with validation of the url
    """
    if check_if_pdf(some_url):
        return {"type": "pdf", "url": some_url, "code": None}
    else:
        if check_if_fullinfo(selenuim_session=selenium_session, some_url=some_url):
            return {"type": "page", "url": some_url, "code": None}
        else:
            selenium_session.get(some_url)
            time.sleep(sleep_time)
            main_body_html = get_html(selenium_session=selenium_session)
            
            messages = []
            messages.append({"role": "assistant", "content": role_message})
            messages.append({"role": "user", "content": user_message.format(main_body_html)})
            response = client.chat.completions.create(
            model=MODEL,
            temperature=0.1,
            messages=messages,
            response_format={ "type": "json_object" }
            )
            response_dict = json.loads(response.choices[0].message.content)
            console.print(response_dict)
            code = response_dict["pdf"]
            return {"type": "pdf", "url": some_url, "code": code}

