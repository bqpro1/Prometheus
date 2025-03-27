import json

with open("prompts/system_prompt.json", "r") as f:
    system_prompts = json.load(f)

print("Available keys in the JSON:")
for key in system_prompts:
    print(f"- {key}")

print("\nTesting search_consideration formatting:")
search_concept = "quantum computing"
try:
    formatted = system_prompts["search_consideration"].format(search_concept)
    print("Formatting successful!")
    print(formatted[:100] + "...")
except KeyError as e:
    print(f"KeyError: {e}")
    # Check the actual format string
    print("Format placeholders in string:")
    import re
    placeholders = re.findall(r'\{([^}]*)\}', system_prompts["search_consideration"])
    print(placeholders)
except Exception as e:
    print(f"Other error: {e}") 