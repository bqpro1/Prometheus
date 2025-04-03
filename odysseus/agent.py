"""
Core agent implementation for Odysseus.

This module contains the OdysseusAgent class which manages the exploration
process, memory tracking, and decision making.
"""

from agents import Agent, Runner
import json
import os
import datetime
import re
from typing import List, Dict, Any, Optional
from colorama import Fore, Style
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from tools.brave_search import BraveSearchTool
from tools.webpage_parser import WebpageParserTool, WebpageExtractLinksTool
from tools.pdf_parser import PDFParserTool
from tools.url_utils import normalize_url, extract_urls_from_text, clean_url
from memory.memory_manager import memorize
import asyncio

# Import prompts from Python modules
from prompts.system_prompt import prompts as SYSTEM_PROMPTS
from prompts.read_prompts import prompts as READ_PROMPTS
from prompts.pdf_prompts import prompts as PDF_PROMPTS
from prompts.search_prompts import prompts as SEARCH_PROMPTS

# Initialize console for rich output
console = Console()

class OdysseusAgent:
    def __init__(self, api_key: str, brave_api_key: str, model_name: str = "gpt-4o"):
        """Initialize Odysseus agent with tools and configuration"""
        self.visited_urls = []
        self.normalized_visited_urls = []  # Store normalized URLs
        self.explored_topics = []  # Track topics we've explored
        self.memory_dir = f"logs/run_odysseus_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Create agent with tools
        self.agent = Agent(
            name="Odysseus",
            instructions=SYSTEM_PROMPTS["navigator_manifest"],
            model=model_name,
            tools=[
                BraveSearchTool(api_key=brave_api_key),
                WebpageParserTool(),
                WebpageExtractLinksTool(),
                PDFParserTool()
            ]
        )
    
    async def run(self, initial_concept: str, max_pages: int = 20):
        """Run the Odysseus agent with an initial concept to explore"""
        print(f"{Style.BRIGHT}{Fore.GREEN}Starting exploration on: {initial_concept}{Style.RESET_ALL}\n")
        
        # Create context to track state between agent executions
        context = {
            "current_url": None,
            "current_concept": initial_concept,
            "visited_urls": self.visited_urls,
            "memory_dir": self.memory_dir
        }
        
        exploration_count = 0
        
        while exploration_count < max_pages:
            exploration_count += 1
            
            # Show progress information
            print(f"{Style.BRIGHT}{Fore.BLUE}[Page {exploration_count}/{max_pages}]{Style.RESET_ALL}")
            
            # Every 5 explorations, suggest exploring a new direction
            if exploration_count % 5 == 0 and self.explored_topics:
                print(f"{Style.BRIGHT}{Fore.MAGENTA}You've explored {exploration_count} pages. Consider exploring new directions.{Style.RESET_ALL}\n")
                
                # Ask the agent to suggest a new topic based on what we've learned
                suggestion_prompt = f"""You've explored several topics so far:
{', '.join(self.explored_topics)}

Suggest a new topic or concept to explore that would complement what you've learned but take your knowledge in a new direction.
Return your suggestion as a simple string (no explanation needed)."""

                suggestion_result = await Runner.run(
                    self.agent,
                    suggestion_prompt,
                    context=context
                )
                
                # Get the suggestion
                if isinstance(suggestion_result.final_output, str):
                    suggestion = suggestion_result.final_output.strip()
                    
                    # Offer the suggestion to the user
                    print(f"{Style.BRIGHT}{Fore.YELLOW}Suggested new direction: {suggestion}{Style.RESET_ALL}")
                    
                    user_input = input(f"{Style.BRIGHT}{Fore.GREEN}Would you like to explore this topic? (y/n): {Style.RESET_ALL}")
                    
                    if user_input.lower() in ['y', 'yes']:
                        context["current_concept"] = suggestion
                        context["current_url"] = None
                        print(f"{Style.BRIGHT}{Fore.GREEN}Exploring new topic: {suggestion}{Style.RESET_ALL}\n")
            
            # If we have a search concept, use Brave Search
            if context["current_concept"] and not context["current_url"]:
                print(f"{Style.BRIGHT}{Fore.BLUE}Searching for: {context['current_concept']}{Style.RESET_ALL}\n")
                
                try:
                    # Construct the prompt for searching
                    search_prompt = SYSTEM_PROMPTS["search_consideration"].format(search_query=context["current_concept"])
                except Exception as e:
                    print(f"Error formatting search prompt: {e}")
                    print(f"SYSTEM_PROMPTS search_consideration: {repr(SYSTEM_PROMPTS['search_consideration'])}")
                    # Fallback to a simple prompt
                    search_prompt = f"Search for information about: {context['current_concept']}. Return a JSON with a 'url' field."
                
                # Run the agent to get search results and decide which to follow
                result = await Runner.run(
                    self.agent, 
                    search_prompt,
                    context=context
                )
                
                # Debug the search result
                print(f"Search result type: {type(result.final_output)}")
                print(f"Search result: {result.final_output}")
                
                # Update context with agent's response - expecting a URL to follow
                if isinstance(result.final_output, dict) and "url" in result.final_output:
                    context["current_url"] = result.final_output["url"]
                    context["current_concept"] = None
                else:
                    # If we didn't get a URL, try to extract it from text response
                    response_text = result.final_output if isinstance(result.final_output, str) else str(result.final_output)
                    
                    # Try to parse as JSON if it's a string that looks like JSON
                    try:
                        if isinstance(response_text, str) and '{' in response_text and '}' in response_text:
                            import json
                            json_start = response_text.find('{')
                            json_end = response_text.rfind('}') + 1
                            json_str = response_text[json_start:json_end]
                            json_data = json.loads(json_str)
                            if "url" in json_data:
                                context["current_url"] = json_data["url"]
                                context["current_concept"] = None
                    except:
                        pass
                        
                    # Find and extract URLs from the text
                    cleaned_urls = extract_urls_from_text(response_text)
                    if cleaned_urls:
                        context["current_url"] = cleaned_urls[0]
                        context["current_concept"] = None
            
            # If we have a URL to explore
            if context["current_url"]:
                url = context["current_url"]
                
                # Clean the URL
                url = clean_url(url)
                context["current_url"] = url
                
                # Normalize the URL for comparison
                normalized_url = normalize_url(url)
                
                # Check if we've already visited this page
                if normalized_url in self.normalized_visited_urls:
                    print(f"{Style.BRIGHT}{Fore.YELLOW}Already visited this page. Looking for a new page to explore.{Style.RESET_ALL}\n")
                    
                    # Ask the agent to choose a new URL
                    next_action_prompt = "You've already visited this page. Please choose a different page to visit or a new search query."
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
                            continue
                        elif "link_to_follow" in result.final_output and result.final_output["link_to_follow"]:
                            context["current_url"] = result.final_output["link_to_follow"]
                            print(f"{Style.BRIGHT}{Fore.YELLOW}Next: Following link to {context['current_url']}{Style.RESET_ALL}\n")
                            continue
                
                print(f"{Style.BRIGHT}{Fore.CYAN}Reading webpage: {url}{Style.RESET_ALL}\n")
                
                # Mark URL as visited
                if url not in self.visited_urls:
                    self.visited_urls.append(url)
                if normalized_url not in self.normalized_visited_urls:
                    self.normalized_visited_urls.append(normalized_url)
                
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
                    
                    # Extract potential topics from the reflection
                    try:
                        # Ask the agent to identify the main topics
                        topic_prompt = "Based on what you just read, identify 1-3 main topics or concepts covered. Respond with a JSON array of strings."
                        topic_result = await Runner.run(
                            self.agent,
                            topic_prompt,
                            context=context
                        )
                        
                        # Try to extract topics from the response
                        if isinstance(topic_result.final_output, str):
                            topics_text = topic_result.final_output
                            
                            # Try to parse JSON array
                            try:
                                if '[' in topics_text and ']' in topics_text:
                                    json_start = topics_text.find('[')
                                    json_end = topics_text.rfind(']') + 1
                                    json_str = topics_text[json_start:json_end]
                                    topics = json.loads(json_str)
                                    
                                    # Add to explored topics
                                    for topic in topics:
                                        if topic and topic not in self.explored_topics:
                                            self.explored_topics.append(topic)
                                    
                                    print(f"{Style.BRIGHT}{Fore.GREEN}Topics identified: {', '.join(topics)}{Style.RESET_ALL}\n")
                            except:
                                pass
                    except:
                        pass
                
                # Ask the agent what to do next - follow a link or search again
                next_action_prompt = SYSTEM_PROMPTS["next_action"].format(
                    visited_urls="\n".join(["- " + u for u in self.visited_urls[-10:]]) if self.visited_urls else "None yet"
                )
                
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
    
    def get_session_summary(self, concept: str, start_time: datetime.datetime, model: str):
        """
        Generate a summary of the exploration session.
        Returns the path to the summary file.
        """
        # Calculate exploration time
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        
        # Generate session summary
        summary_file = os.path.join(self.memory_dir, "session_summary.md")
        
        with open(summary_file, "w") as f:
            f.write(f"# Odysseus Exploration Summary\n\n")
            f.write(f"**Initial concept:** {concept}\n")
            f.write(f"**Date:** {start_time.strftime('%Y-%m-%d')}\n")
            f.write(f"**Duration:** {duration}\n")
            f.write(f"**Model used:** {model}\n\n")
            
            f.write(f"## Pages Visited ({len(self.visited_urls)})\n\n")
            for i, url in enumerate(self.visited_urls, 1):
                f.write(f"{i}. [{url}]({url})\n")
            
            f.write(f"\n## Topics Explored\n\n")
            for topic in self.explored_topics:
                f.write(f"- {topic}\n")
        
        return summary_file 