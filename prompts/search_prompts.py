"""
Search-related prompts for the Odysseus agent.
These prompts define how the agent processes search results and selects links to explore.
"""

# Prompt for traditional search interface with numbered results
search_consideration = """Given the search phrase {search_query} and following snippets of the links: 
{search_results}
 Give me the link number to follow. Format your answer in markdown as follows:
link_num: 1"""

# Prompt for API-based search results in JSON format
search_consideration_api = """Given the search phrase {search_query} and the {result_count} following results as list of jsons:

{search_results_json}

Which link would you like to follow? Make resonable decision. Read all the snippets and return the choosen json. Do not return anything else."""

# Export all prompts as a dictionary for backwards compatibility with JSON loading
prompts = {
    "search_consideration": search_consideration,
    "search_consideration_api": search_consideration_api
} 