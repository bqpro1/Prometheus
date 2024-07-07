
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from trafilatura import extract
from config import Config
import tiktoken
from typing import List, Any
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools import BraveSearch
from langchain_community.utilities import BingSearchAPIWrapper
from colorama import Fore, Style

ENCODING = tiktoken.encoding_for_model(Config.MODEL_NAME)
PDF_PROMPTS = json.load(open(Config.PDF_PROMPT_PATH, "r")) 
MODEL = Config.MODEL_NAME
load_dotenv()
API_KEY = os.getenv("API_KEY")
BRAVE_KEY = os.getenv("BRAVE_KEY")
client = OpenAI(api_key=API_KEY)




def get_page_source(selenium_session: webdriver,
                    some_url: str,
                    sleep_time: int=5) -> str:
    """
    Returns the page source of a given url
    """
    try:
        selenium_session.get(some_url)
        time.sleep(sleep_time)
        page_source = selenium_session.page_source
        return page_source
    except Exception as e:
        print(e)
        return None


def search_info(selenium_session: webdriver, 
                search_concept: str,
                visited_urls: List[str]) -> tuple:
    """
    Returns the links of a given search concept using a search engine
    """
    search_engine = Config.SERCH_ENGINE
    selenium_session.get(search_engine)
    try:
        searchbox = selenium_session.find_element(by=Config.SEARCH_INPUT_CLASSIC["by"], 
                                                        value=Config.SEARCH_INPUT_CLASSIC["value"])
    except:
        searchbox = selenium_session.find_element(by=Config.SEARCH_INPUT_INPUT["by"], 
                                                        value=Config.SEARCH_INPUT_INPUT["value"])
    searchbox.send_keys(search_concept)
    searchbox.send_keys(Keys.ENTER)
    results = selenium_session.find_element(by=Config.SEARCH_RESULTS["by"], 
                                                   value=Config.SEARCH_RESULTS["value"])
    search_links = results.find_elements(by=Config.SEARCH_LINKS["by"], 
                                  value=Config.SEARCH_LINKS["value"])
    
    search_links = [{"text": link.text,
                     "link": link,
                     "adress": link.find_element(by=Config.LINKS_ADRESS["by"],
                                                 value=Config.LINKS_ADRESS["value"]).get_attribute("href")} for link in search_links]
    search_links = [link for link in search_links if link["adress"] not in visited_urls]
    
    link_synopsis = "\n".join([f"{i+1}. {link['text']}" for i, link in enumerate(search_links)])
    return (search_links, link_synopsis)


def search_api(search_concept: str, 
           num_results: int = 10):
    """
    Uses given search engine to look for a given concept by API
    """
    sercher = BraveSearch.from_api_key(api_key=BRAVE_KEY,
                                    search_kwargs={"count": num_results})
    search = json.loads(sercher.run(search_concept))
    return search


def get_links(selenium_session: webdriver):
    """
    Returns the links of a given page source
    """
    links = selenium_session.find_elements(by="tag name", value="a")
    return links
        

def text_extract(page_source: str, 
                 token_limit: int = 128000, 
                 text_cut: int = 100000) -> str:
    
    """
    Returns the text of a given page source
    """
    try:
        full_text = extract(page_source)
        token_num = len(ENCODING.encode(full_text))
        if token_num >= token_limit:
            text = full_text[:text_cut]
        else:
            text = full_text
        return text
    except Exception as e:
        print(e)
        return None


def decide_SearchorLinks(link_num: str, what_to_search: str):
    """
    Returns dict with decision of what to search or what link to click 
    """
    decision = {"what_to_search": what_to_search,
                "link_num": link_num}
    return decision

def check_if_pdf(some_url: str) -> bool:
    """
    Returns bool if the page is a pdf
    """
    try:
        loader = PyPDFLoader(some_url)
        loader.load_and_split()
        print(Fore.LIGHTCYAN_EX + "The page is a pdf")                      
        return True
    except:
        print(Fore.LIGHTCYAN_EX + "The page is not a pdf")
        return False


def check_if_fullinfo(selenuim_session: webdriver,
                      some_url: str,
                      sleep_time: int=5) -> bool:

    """
    Returns bool if the page is a pdf abstract
    """

    try:
        selenuim_session.get(some_url)
        time.sleep(sleep_time)
        main_body_html = get_html(selenuim_session)
        messages = [{"role": "system",
                 "content": [
                     {"type": "text", "text": PDF_PROMPTS["role"]}
                    ]},
                    {"role": "user",
                     "content": [
                         {"type": "text", "text": PDF_PROMPTS["full_info"].format(selenuim_session.current_url, 
                                                                                    main_body_html,
                                                                                    PDF_PROMPTS["json_page2pdf"])}
                                ]
                    }
                    ]
        
        response = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=messages,
        response_format={ "type": "json_object" }
        )
        response_dict = json.loads(response.choices[0].message.content)
        if response_dict["full_info"]:
            print(Fore.LIGHTCYAN_EX + "The page is a full info")
            return True
        else:
            print(Fore.LIGHTCYAN_EX + "The page is not a full info")
            return False
    except Exception as e:
        print(e)
        return None

def get_html(selenium_session: webdriver,
             token_limit: int = 128000,
             text_cut: int = 100000) -> str:
    """
    Returns the html of a given selenium session
    """
    full_html = selenium_session.page_source
    token_num = len(ENCODING.encode(full_html))
    if token_num >= token_limit:
        html_text = full_html[:text_cut]
    else:
        html_text = full_html
    return html_text        

def limit_text(text: str,
               token_limit: int = 128000,
               text_cut: int = 100000) -> str:
    """
    Returns the text cut to the token limit
    """
    token_num = len(ENCODING.encode(text))
    if token_num >= token_limit:
        text = text[:text_cut]
        print(Fore.YELLOW + "The text was cut to the token limit")
    else:
        print(Fore.YELLOW + "The text was not cut")
        pass
    return text
                 