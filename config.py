
from attr import dataclass

@dataclass
class Config:
    USER_AGENTS_PATH = "data/user_agents.json"
    SERCH_ENGINE = "https://duckduckgo.com/"
    SEARCH_INPUT = {"by": "id", "value": "searchbox_input"}
    SEARCH_RESULTS = {"by": "id", "value": "react-layout"}
    SEARCH_LINKS = {"by": "tag name", "value": "li"}
    LINKS_ADRESS = {"by": "tag name", "value": "a"}
    MODEL_NAME = "gpt-3.5-turbo-16k-0613"