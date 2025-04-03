#!/usr/bin/env python
"""
Command-line interface for the Odysseus agent.

This module provides a command-line interface for running the Odysseus agent,
including argument parsing and environment setup.
"""

import asyncio
import datetime
import os
from colorama import Fore, Style
from dotenv import load_dotenv
from fire import Fire

from odysseus.agent import OdysseusAgent

def run_odysseus(concept: str = None, model: str = "gpt-4o", max_pages: int = 20):
    """
    Command line entry point for Odysseus agent.
    
    Args:
        concept: The initial concept to explore. If None, will prompt the user.
        model: The model name to use for the agent.
        max_pages: Maximum number of pages to explore.
    """
    # Load environment variables
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
    brave_api_key = os.getenv("BRAVE_API_KEY") or os.getenv("BRAVE_KEY")
    
    # Check for required API keys
    if not openai_api_key:
        print(f"{Style.BRIGHT}{Fore.RED}Error: OPENAI_API_KEY environment variable is not set.{Style.RESET_ALL}")
        print("Please set it in your .env file or environment variables.")
        return
        
    if not brave_api_key:
        print(f"{Style.BRIGHT}{Fore.RED}Error: BRAVE_API_KEY environment variable is not set.{Style.RESET_ALL}")
        print("Please set it in your .env file or environment variables.")
        return
    
    # Prompt for a concept if not provided
    if not concept:
        concept = input(f"{Fore.GREEN}{Style.BRIGHT}What concept should I explore? {Style.RESET_ALL}")
    
    # Create the agent
    agent = OdysseusAgent(
        api_key=openai_api_key,
        brave_api_key=brave_api_key,
        model_name=model
    )
    
    # Track time for summary
    start_time = datetime.datetime.now()
    
    try:
        # Run the agent with a page limit
        asyncio.run(agent.run(concept, max_pages=max_pages))
    except KeyboardInterrupt:
        print(f"\n{Style.BRIGHT}{Fore.YELLOW}Exploration stopped by user.{Style.RESET_ALL}")
    finally:
        # Generate and display session summary
        summary_file = agent.get_session_summary(concept, start_time, model)
        
        print(f"\n{Style.BRIGHT}{Fore.GREEN}Exploration session complete! Summary saved to: {summary_file}{Style.RESET_ALL}")
        print(f"Visited {len(agent.visited_urls)} pages and explored {len(agent.explored_topics)} topics.")

if __name__ == "__main__":
    Fire(run_odysseus) 