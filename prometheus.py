from dotenv import load_dotenv
from reading import read
from searching import search
from session_manager import start_session
from fire import Fire
from typing import List
from colorama import Fore, Style
from openai import OpenAI
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=API_KEY)


def run_prometheus(headless: bool,
                    visited_urls: List[str] = [], 
                    request_sep: str = "?"):
    """
    Runs the Prometheus bot
    """

    actual_url = input(Fore.GREEN + Style.BRIGHT + "What is the url you want to start from? ")
    readS = start_session(headless=headless)
    searchS = start_session(headless=headless)

    while True:
        
        concept = read(selenium_session=readS,
                       openai=client,
                       reading_url=actual_url)
        
        if request_sep in actual_url:
            actual_url = actual_url.split("?")[0]
        else:
            pass
        visited_urls.append(actual_url)
        if concept["link2follow"]:
            actual_url = concept["link2follow"]
        elif concept["search_for"]:
            concept = concept["search_for"]
            
            link2content4read = search(selenium_session=searchS, 
                                       openai=client, 
                                       search_concept=concept, 
                                       visited_urls=visited_urls)
            actual_url = link2content4read

if __name__ == "__main__":
    Fire(run_prometheus)