from reading import read
from searching_api import search
from session_manager import start_session
from config import Config
from fire import Fire
from typing import List
from colorama import Fore, Style
from openai import OpenAI
import os
import datetime
import dotenv

dotenv.load_dotenv()
MEMORY_LOGS_PATH = Config.MEMORY_LOGS_PATH
API_KEY = os.getenv("API_KEY")

client = OpenAI(api_key=API_KEY)


def run_prometheus(headless: bool,
                   visited_urls: List[str] = [],
                   request_sep: str = "?",
                   mem_path: str = MEMORY_LOGS_PATH):
    """
    Runs the Prometheus bot
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    mem_dir = f"logs/run_prometheus_{now}"
    os.makedirs(mem_dir)
    concept = input(Fore.GREEN + Style.BRIGHT + "What is the problem I should learn about: ")
    readS = start_session(headless=headless)
    actual_url = search(search_concept=concept,
                        openai=client,
                        visited_urls=visited_urls)
    
    while True:
        
        concept = read(selenium_session=readS,
                       openai=client,
                       reading_url=actual_url,
                       mem_dir=mem_dir)
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