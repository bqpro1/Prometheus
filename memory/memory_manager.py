import os
import datetime
from typing import Dict, Any, Optional, List
import json
from urllib.parse import urlparse

def memorize(raw_memories: str, 
             page_url: str,
             mem_dir: str) -> str:
    """
    Stores memories from browsing in a markdown file
    
    Args:
        raw_memories: The text content of the memory to store
        page_url: The URL of the page that generated this memory
        mem_dir: Directory to store memory files
        
    Returns:
        Path to the stored memory file
    """
    # Create a sanitized filename from the URL
    parsed_url = urlparse(page_url)
    domain = parsed_url.netloc
    path = parsed_url.path.replace('/', '_')
    
    # Use a timestamp to ensure uniqueness
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a filename that is descriptive but safe
    filename = f"{domain}{path}_{timestamp}.md"
    # Ensure no characters that would be invalid in a filename
    filename = ''.join(c if c.isalnum() or c in ['_', '-', '.'] else '_' for c in filename)
    
    # Create the full path
    file_path = os.path.join(mem_dir, filename)
    
    # Write the memory content
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"# Memory from {page_url}\n\n")
        file.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n\n")
        file.write(raw_memories)
        file.write("\n\n")
        file.write(f"Source: {page_url}")
        
    print(f"Memory stored at {file_path}")
    return file_path

def get_memories(mem_dir: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent memories from the memory directory
    
    Args:
        mem_dir: Directory containing memory files
        limit: Maximum number of memories to return
        
    Returns:
        List of memory objects with content and metadata
    """
    if not os.path.exists(mem_dir):
        return []
        
    # Get all markdown files in memory directory
    memory_files = [f for f in os.listdir(mem_dir) if f.endswith('.md')]
    
    # Sort by modification time (most recent first)
    memory_files.sort(key=lambda f: os.path.getmtime(os.path.join(mem_dir, f)), reverse=True)
    
    # Limit the number of files
    memory_files = memory_files[:limit]
    
    memories = []
    for file_name in memory_files:
        file_path = os.path.join(mem_dir, file_name)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Extract source URL from the last line
        lines = content.split('\n')
        source_url = ""
        for line in reversed(lines):
            if line.startswith("Source: "):
                source_url = line[8:]  # Remove "Source: " prefix
                break
                
        memories.append({
            "content": content,
            "source_url": source_url,
            "timestamp": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        })
        
    return memories 