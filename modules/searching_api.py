import json
from config import Config
from actions import search_api
from openai import OpenAI
from colorama import Fore, Style
import time


READ_PROMPTS = json.load(open(Config.READ_PROMPT_PATH, "r"))
SEARCH_PROMPTS = json.load(open(Config.SEARCH_PROMPT_PATH, "r"))
model = Config.MODEL_NAME

def search(search_concept: str,
           openai: OpenAI, 
           visited_urls: list,
           temp: float = 0.5) -> str:
    """
    Uses given search engine to look for a given concept
    """
    print(Style.BRIGHT + Fore.LIGHTWHITE_EX + f"I am looking for info about {search_concept}", end="\n\n")
    results = search_api(search_concept)
    filtered_results = [result for result in results if result["link"] not in visited_urls]
    len_results = str(len(filtered_results))

    search_messages = [{"role": "system",
                     "content": [
                          {"type": "text", "text": READ_PROMPTS["navigator_manifest"]}
                    ]},
                    {"role": "user",
                     "content": [
                          {"type": "text", "text": SEARCH_PROMPTS["search_consideration_api"].format(search_concept, len_results, filtered_results)}
                    ]}]        
            
    raw_decision = openai.chat.completions.create(
        model=model,
        temperature=temp,
        messages=search_messages,
        response_format={ "type": "json_object" }
    )

    decision = json.loads(raw_decision.choices[0].message.content)
    print(Style.BRIGHT + Fore.LIGHTWHITE_EX + f"I will follow this:\n{decision['title']}\n{decision['snippet']}", end="\n\n")
    link2follow = decision["link"]
    return link2follow
