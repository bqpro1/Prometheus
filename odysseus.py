from modules.reading import read, read_pdf
from modules.validator import validate
from modules.searching_api import search
from session_manager import start_session
from selenium.webdriver.common.by import By
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
    driver = start_session(headless=headless)
    actual_url = search(search_concept=concept,
                        openai=client,
                        visited_urls=visited_urls)
    
    while True:
        
        Content4Reading = validate(selenium_session=driver,
                                   some_url=actual_url)
        #PDF CASE!
        if Content4Reading["type"] == "pdf":
            # PURE PDF CASE!
            if not Content4Reading["code"]:
                concept = read_pdf(selenium_session=driver,
                                   openai=client,
                                   reading_url=actual_url,
                                   mem_dir=mem_dir)
                if request_sep in actual_url:
                    actual_url = actual_url.split("?")[0]
                else:
                    pass
                visited_urls.append(actual_url)
                concept = concept["search_for"]
                actual_url = search(search_concept=concept,
                                                    openai=client,
                                                    visited_urls=visited_urls)
            # PDF WITH CODE CASE!
            else:
                print(Style.BRIGHT + Fore.GREEN + "CODE: " + Content4Reading["code"])
                try:
                    pdf_url = driver.find_element(By.XPATH, Content4Reading["code"]).get_attribute("href")
                    actual_url = pdf_url
                    concept = read_pdf(selenium_session=driver,
                                    openai=client,
                                    reading_url=actual_url,
                                    mem_dir=mem_dir)
                    if request_sep in actual_url:
                        actual_url = actual_url.split("?")[0]
                    else:
                        pass
                    visited_urls.append(actual_url)
                    concept = concept["search_for"]
                    actual_url = search(search_concept=concept,
                                    openai=client,
                                    visited_urls=visited_urls)
                except Exception as e:
                    print(e)
                    print(Style.BRIGHT + Fore.RED + "The code could not be executed")
                    if request_sep in actual_url:
                        actual_url = actual_url.split("?")[0]
                    else:
                        pass
                    visited_urls.append(actual_url)
                    actual_url = search(search_concept=concept,
                                    openai=client,
                                    visited_urls=visited_urls)
        #PAGE CASE!
        else:
            concept = read(selenium_session=driver,
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