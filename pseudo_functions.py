
should_search = [
        {
            "name": "decide_SearchorLinks",
            "description": "Returns dict with decision.",
            "parameters": {
                "type": "object",
                "properties": {
                    "what_to_search": {
                        "type": "string",
                        "description": "Query to search for",
                    },
                    "link_num": {"type": "string", "description": "Link number to click"},
                },
                "required": ["what_to_search", "link_num"],
            },
        }
    ]