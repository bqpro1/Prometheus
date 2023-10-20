
import openai
from selenium import webdriver
from actions import get_page_source, get_links, text_extract
import json
from memory import MEMORIES, structure_memory
from config import Config
from pseudo_functions import should_search
from colorama import Fore, Style

READ_PROMPTS = json.load(open("read_prompts.json", "r"))
model = Config.MODEL_NAME

def read(selenium_session: webdriver, reading_url: str, link_limit: int = 100):
    
    page_source = get_page_source(selenium_session=selenium_session, some_url=reading_url)
    text = text_extract(page_source)

    print(Style.BRIGHT+Fore.BLUE + f"I am reading the following page: {reading_url}", end="\n\n")
    
    links = get_links(selenium_session)
    links_to_follow = [(l.accessible_name, l.get_attribute("href")) for l in links if l.get_attribute("href") and l.accessible_name]
    if len(links_to_follow) > link_limit:
        links_to_follow = links_to_follow[:link_limit]
    texted_links_to_follow = "\n".join([f"{i+1}. {link[0]}, {link[1]}" for i, link in enumerate(links_to_follow)])

    messages = [{"role": "system", "content": READ_PROMPTS["navigator_manifest"]},
                {"role": "user", "content": READ_PROMPTS["reflection"].format(reading_url, text)}]


    # Generates memories from the content of the page
    raw_page_memories = openai.ChatCompletion.create(
        model=model,
        temperature=0.8,
        messages=messages
    )

    page_memories = raw_page_memories["choices"][0]["message"]["content"]
    
    print(Style.BRIGHT + Fore.LIGHTGREEN_EX + page_memories, end="\n\n")
    
    MEMORIES["theses"].append(structure_memory(page_memories, reading_url))
    
    messages.append({"role": "assistant", "content": page_memories})
    messages.append({"role": "user", "content": READ_PROMPTS["autoreflection"].format(page_memories)})


    # Generates the question to ask
    generated_question = openai.ChatCompletion.create(
        model=model,
        temperature=0.8,
        messages=messages
    )


    current_question = generated_question["choices"][0]["message"]["content"]
    
    print(Style.BRIGHT + Fore.YELLOW + current_question, end="\n\n")
    
    MEMORIES["questions"].append({reading_url: current_question})
    messages.append({"role": "assistant", "content": current_question})
    messages.append({"role": "user", "content": READ_PROMPTS["next_move_consideration"].format(current_question,
                                                                            texted_links_to_follow,
                                                                            Config.SERCH_ENGINE)})


    # Make decision about the futher steps
    filtered_messages = [messages[0], messages[-1]]
    raw_decision = openai.ChatCompletion.create(
        model=model,
        temperature=0.8,
        messages=filtered_messages,
        functions=should_search,
        function_call="auto"
    )

    decision_message = raw_decision["choices"][0]["message"]
    if decision_message.get("function_call"):
        decision = json.loads(decision_message["function_call"]["arguments"])
        if decision.get("link_num"):
            print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX +  f"follow link: {decision['link_num']}", end="\n\n")
            return {"search_for": None, "link2follow":links_to_follow[int(decision["link_num"]) - 1][1]}
        else:
            print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + f"Searching for: {decision['what_to_search']}", end="\n\n")
            return {"search_for": decision["what_to_search"], "link2follow": None}