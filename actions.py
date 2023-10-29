
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from trafilatura import extract
from config import Config
import tiktoken
from typing import List

ENCODING = tiktoken.encoding_for_model(Config.MODEL_NAME)


def get_page_source(selenium_session: webdriver, some_url: str, sleep_time: int=1):
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


def search_info(selenium_session: webdriver, search_concept: str, visited_urls: List[str]):
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
    return search_links, link_synopsis


def get_links(selenium_session: webdriver):
    """
    Returns the links of a given page source
    """
    links = selenium_session.find_elements(by="tag name", value="a")
    return links
        

def text_extract(page_source: str, 
                 token_limit: int = 10000, 
                 text_cut: int = 50000):
    
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