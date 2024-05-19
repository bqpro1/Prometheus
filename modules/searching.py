from actions import search_info
from config import Config
from colorama import Fore, Style
import json
from openai import OpenAI
from selenium import webdriver
from typing import List

READ_PROMPTS = json.load(open(Config.READ_PROMPT_PATH, "r"))
SEARCH_PROMPTS = json.load(open(Config.SEARCH_PROMPT_PATH, "r"))
model = Config.MODEL_NAME


def search(selenium_session: webdriver,
           openai: OpenAI, 
           search_concept: str,
           visited_urls: List[str]):
    """
    Uses given search engine to look for a given concept
    """
    
    selenium_session.get(Config.SERCH_ENGINE)
    selenium_session.implicitly_wait(10)
    print(Style.BRIGHT + Fore.LIGHTWHITE_EX + f"I am looking for info about {search_concept}", end="\n\n")
    
    search_links, link_synopsis = search_info(selenium_session, 
                                              search_concept, 
                                              visited_urls)


    search_messages = [{"role": "system", "content": READ_PROMPTS["navigator_manifest"]},
                {"role": "user", "content": SEARCH_PROMPTS["search_consideration"].format(search_concept, link_synopsis)}]

    raw_search_link_num = openai.chat.completions.create(
        model=model,
        temperature=0.8,
        messages=search_messages
    )

    search_link_num = raw_search_link_num.choices[0].message.content
    
    assert search_link_num[-1].isdigit()
    link_index = int(search_link_num[-1])

    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + f"I'll follow this link: {search_links[link_index - 1]['text']}", end="\n\n")

    search_links[link_index - 1]["link"].click()

    link2read = selenium_session.current_url
    return link2read
    