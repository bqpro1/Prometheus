from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "ollama/llama3",
        "temperature": 0,
        "format": "",  # Ollama needs the format to be specified explicitly
        "base_url": "http://localhost:11434",  # set Ollama URL
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://localhost:11434",  # set Ollama URL
    }
}

smart_scraper_graph = SmartScraperGraph(
    prompt="Summarize the following webpage.",
    # also accepts a string with the already downloaded HTML code
    source="https://en.wikipedia.org/wiki/Deontic_logic",
    config=graph_config)

result = smart_scraper_graph.run()
print(result)