from reading import read
from searching import search
from session_manager import start_session
from fire import Fire
from typing import List
from colorama import Fore, Style
import openai
import json

config = json.load(open("/Users/leszekbukowski/openai/config.json", "r"))
openai.api_key = config["KEY"]

def run_prometheus(visited_urls: List[str] = []):
    """
    Runs the Prometheus bot
    """

    actual_url = input(Fore.GREEN + Style.BRIGHT + "What is the url you want to start from? ")
    readS = start_session(headless=True)
    searchS = start_session(headless=True)

    while True:
        concept = read(readS, actual_url)
        if "?" in actual_url:
            actual_url = actual_url.split("?")[0]
        else:
            pass
        visited_urls.append(actual_url)
        if concept["link2follow"]:
            actual_url = concept["link2follow"]
        elif concept["search_for"]:
            concept = concept["search_for"]
            link2content4read = search(searchS, concept, visited_urls)
            actual_url = link2content4read

if __name__ == "__main__":
    Fire(run_prometheus)

