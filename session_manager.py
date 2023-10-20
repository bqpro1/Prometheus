from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config import Config
import json
from random import choice

USER_AGENTS = json.loads(open(Config.USER_AGENTS_PATH).read())["user_agents"]

def start_session(headless=True):
    """
    Returns the page source of a given url
    """
    options = Options()
    service = Service()
    if headless:
        options.add_argument("--headless")
    else:
        pass
    options.add_argument(f"user-agent={choice(USER_AGENTS)}")
    session = webdriver.Chrome(service=service,options=options)
    return session