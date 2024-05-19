import os
import datetime

def memorize(raw_memories: str, 
             page_url: str,
             mem_dir: str):
    """
    Memorizes the content of a page
    """
    filename = f"{page_url.split('/')[-1]}.md"
    file_path = os.path.join(mem_dir, filename)
    with open(file_path, 'w') as file:
        file.write(raw_memories)
        file.write("\n\n")
        file.write(f"Page: {page_url}")
        file.close()

