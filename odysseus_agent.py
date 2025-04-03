from agents import Agent, Runner
import json
import os
import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from colorama import Fore, Style
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from tools.brave_search import BraveSearchTool
from tools.webpage_parser import WebpageParserTool, WebpageExtractLinksTool
from tools.pdf_parser import PDFParserTool
from memory.memory_manager import memorize
import asyncio
from fire import Fire

# Import prompts from Python modules
from prompts.system_prompt import prompts as SYSTEM_PROMPTS
from prompts.read_prompts import prompts as READ_PROMPTS
from prompts.pdf_prompts import prompts as PDF_PROMPTS
from prompts.search_prompts import prompts as SEARCH_PROMPTS

# Initialize console for rich output
console = Console()

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY") or os.getenv("BRAVE_KEY")

# No longer need to load JSON files
# with open("prompts/system_prompt.json", "r") as f:
#     SYSTEM_PROMPTS = json.load(f)

class OdysseusAgent:
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize Odysseus agent with tools and configuration"""
        self.visited_urls = []
        self.memory_dir = f"logs/run_odysseus_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Create agent with tools
        self.agent = Agent(
            name="Odysseus",
            instructions=SYSTEM_PROMPTS["navigator_manifest"],
            model=model_name,
            tools=[
                BraveSearchTool(api_key=BRAVE_API_KEY),
                WebpageParserTool(),
                WebpageExtractLinksTool(),
                PDFParserTool()
            ]
        )
    
    async def run(self, initial_concept: str):
        """Run the Odysseus agent with an initial concept to explore"""
        print(f"{Style.BRIGHT}{Fore.GREEN}Starting exploration on: {initial_concept}{Style.RESET_ALL}\n")
        
        # Create context to track state between agent executions
        context = {
            "current_url": None,
            "current_concept": initial_concept,
            "visited_urls": self.visited_urls,
            "memory_dir": self.memory_dir
        }
        
        while True:
            # If we have a search concept, use Brave Search
            if context["current_concept"] and not context["current_url"]:
                print(f"{Style.BRIGHT}{Fore.BLUE}Searching for: {context['current_concept']}{Style.RESET_ALL}\n")
                
                # Construct the prompt for searching
                search_prompt = SYSTEM_PROMPTS["search_consideration"].format(search_query=context["current_concept"])
                
                # Run the agent to get search results and decide which to follow
                result = await Runner.run(
                    self.agent, 
                    search_prompt,
                    context=context
                )
                
                # Update context with agent's response - expecting a URL to follow
                if isinstance(result.final_output, dict) and "url" in result.final_output:
                    context["current_url"] = result.final_output["url"]
                    context["current_concept"] = None
                else:
                    # If we didn't get a URL, try to extract it from text response
                    response_text = result.final_output if isinstance(result.final_output, str) else str(result.final_output)
                    # Find a URL in the text (simple extraction, could be improved)
                    import re
                    urls = re.findall(r'https?://\S+', response_text)
                    if urls:
                        context["current_url"] = urls[0]
                        context["current_concept"] = None
            
            # If we have a URL to explore
            if context["current_url"]:
                url = context["current_url"]
                print(f"{Style.BRIGHT}{Fore.CYAN}Reading webpage: {url}{Style.RESET_ALL}\n")
                
                # Mark URL as visited
                if url not in self.visited_urls:
                    self.visited_urls.append(url)
                context["visited_urls"] = self.visited_urls
                
                # Construct the prompt for reading the page
                reading_prompt = SYSTEM_PROMPTS["reflection"].format(current_url=url)
                
                # Run the agent to read and analyze the page
                result = await Runner.run(
                    self.agent, 
                    reading_prompt,
                    context=context
                )
                
                # Memorize the agent's reflection on the content
                if isinstance(result.final_output, str):
                    memorize(raw_memories=result.final_output, page_url=url, mem_dir=self.memory_dir)
                    console.print(Panel(Markdown(result.final_output)))
                
                # Ask the agent what to do next - follow a link or search again
                next_action_prompt = SYSTEM_PROMPTS["next_action"]
                
                result = await Runner.run(
                    self.agent, 
                    next_action_prompt,
                    context=context
                )
                
                # Update context based on agent's decision
                if isinstance(result.final_output, dict):
                    if "search_for" in result.final_output and result.final_output["search_for"]:
                        context["current_concept"] = result.final_output["search_for"]
                        context["current_url"] = None
                        print(f"{Style.BRIGHT}{Fore.YELLOW}Next: Searching for {context['current_concept']}{Style.RESET_ALL}\n")
                    elif "link_to_follow" in result.final_output and result.final_output["link_to_follow"]:
                        context["current_url"] = result.final_output["link_to_follow"]
                        print(f"{Style.BRIGHT}{Fore.YELLOW}Next: Following link to {context['current_url']}{Style.RESET_ALL}\n")
                    else:
                        print(f"{Style.BRIGHT}{Fore.RED}Unclear next action. Starting new search.{Style.RESET_ALL}\n")
                        context["current_concept"] = initial_concept
                        context["current_url"] = None
                else:
                    print(f"{Style.BRIGHT}{Fore.RED}Invalid response format. Starting new search.{Style.RESET_ALL}\n")
                    context["current_concept"] = initial_concept
                    context["current_url"] = None

def run_odysseus(concept: str = None, model: str = "gpt-4o"):
    """Command line entry point for Odysseus agent"""
    if not concept:
        concept = input(f"{Fore.GREEN}{Style.BRIGHT}What concept should I explore? {Style.RESET_ALL}")
    
    agent = OdysseusAgent(model_name=model)
    asyncio.run(agent.run(concept))

if __name__ == "__main__":
    Fire(run_odysseus) 