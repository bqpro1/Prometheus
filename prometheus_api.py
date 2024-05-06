from dotenv import load_dotenv
from reading import read
from searching_api import search
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

    concept = input(Fore.GREEN + Style.BRIGHT + "What is the problem I should learn about: ")
    readS = start_session(headless=headless)
    actual_url = search(search_concept=concept,
                        openai=client,
                        visited_urls=visited_urls)
    
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
             actual_url = search(search_concept=concept,
                                 openai=client,
                                 visited_urls=visited_urls)

if __name__ == "__main__":
    Fire(run_prometheus)