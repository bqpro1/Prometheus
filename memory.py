from datetime import datetime

MEMORIES = {"questions": [], "theses": []}

def structure_memory(raw_thesis: str, page_url: str):
    theses = [thesis[2:].strip() for thesis in raw_thesis.split("\n")]
    timed_theses = {page_url: [{"memory": thesis, "time": datetime.now().isoformat()[:-7]} for thesis in theses]}
    return timed_theses

