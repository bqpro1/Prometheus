
from attr import dataclass

@dataclass
class Config:
    USER_AGENTS_PATH = "data/user_agents.json"
    SERCH_ENGINE = "https://duckduckgo.com/"
    SEARCH_INPUT_CLASSIC = {"by": "id", "value": "searchbox_input"}
    SEARCH_INPUT_INPUT = {"by": "id", "value": "search_form_input_homepage"}
    SEARCH_RESULTS = {"by": "id", "value": "react-layout"}
    SEARCH_LINKS = {"by": "tag name", "value": "li"}
    LINKS_ADRESS = {"by": "tag name", "value": "a"}
    MODEL_NAME = "gpt-4o"
    READ_PROMPT_PATH = "prompts/read_prompts.json"
    SEARCH_PROMPT_PATH = "prompts/search_prompts.json"
    PDF_PROMPT_PATH = "prompts/pdf_prompts.json"
    MEMORY_LOGS_PATH = "logs/"