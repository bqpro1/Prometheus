import openai
import json
from config import Config

config = json.load(open("/Users/leszekbukowski/openai/config.json", "r"))
openai.api_key = config["KEY"]

model = Config.MODEL_NAME