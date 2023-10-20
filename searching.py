from actions import search_info
from config import Config
from colorama import Fore, Style
import json
import openai
from selenium import webdriver
from time import sleep

READ_PROMPTS = json.load(open("read_prompts.json", "r"))
SEARCH_PROMPTS = json.load(open("search_prompts.json", "r"))
model = Config.MODEL_NAME

def search(selenium_session: webdriver, 
           search_concept: str,
           context_link: str):
    
    selenium_session.get(Config.SERCH_ENGINE)
    sleep(10)
    print(Style.BRIGHT + Fore.LIGHTWHITE_EX + f"I am looking for info about {search_concept}", end="\n\n")
    
    search_links, link_synopsis = search_info(selenium_session, 
                                              search_concept, 
                                              context_link)


    search_messages = [{"role": "system", "content": READ_PROMPTS["navigator_manifest"]},
                {"role": "user", "content": SEARCH_PROMPTS["search_consideration"].format(search_concept, link_synopsis)}]

    raw_search_link_num = openai.ChatCompletion.create(
        model=model,
        temperature=0.8,
        messages=search_messages
    )

    search_link_num = raw_search_link_num["choices"][0]["message"]["content"]
    
    #print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + search_link_num, end="\n\n")
    
    assert search_link_num[-1].isdigit()
    link_index = int(search_link_num[-1])

    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + f"I'll follow this link: {search_links[link_index - 1]['text']}", end="\n\n")

    search_links[link_index - 1]["link"].click()

    link2read = selenium_session.current_url
    return link2read
    