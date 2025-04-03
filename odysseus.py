import asyncio
import os
from typing import Optional, Set

import dotenv
from fire import Fire
# Assuming these imports from the SDK are relevant
from openai_agents import Agent, Runner, WebSearchTool, Message
from pydantic import BaseModel

# --- Assumed imports for your custom agent and tools ---
# You need to ensure these files and classes exist and are correctly defined.
# Example:
# from odysseus_agent import OdysseusAgent # Your main agent definition
# from tools.web_reader import WebReaderTool # Your tool for reading web pages
# from tools.pdf_reader import PdfReaderTool # Your tool for reading PDFs

dotenv.load_dotenv()
# OPENAI_API_KEY should be set as an environment variable for the SDK

# --- Define the expected output structure for the agent ---
class NextStep(BaseModel):
    """Defines the next action for the agent: follow a URL or search."""
    next_url: Optional[str] = None
    search_query: Optional[str] = None
    reasoning: str # Agent should explain its choice

# --- Placeholder Agent Definition ---
# Replace this with the import of your actual OdysseusAgent
# Ensure your OdysseusAgent is configured with necessary tools and outputs NextStep
class PlaceholderOdysseusAgent(Agent):
    def __init__(self):
        super().__init__(
            name="OdysseusExplorer",
            instructions="""You are an autonomous web explorer. Given a starting URL or search concept,
            analyze the provided content (using available tools like web reader, PDF reader).
            Decide the next best step to continue exploration: either follow a relevant link found in the content,
            or formulate a new search query based on your understanding.
            Avoid revisiting URLs listed in the 'visited_urls' list within the prompt.
            Output your decision (next_url or search_query) and reasoning clearly in the specified format.""",
            tools=[WebSearchTool()], # Add your WebReaderTool, PdfReaderTool etc. here
            output_type=NextStep
        )

# Use your actual agent here
agent = PlaceholderOdysseusAgent()
# agent = OdysseusAgent() # <-- Uncomment this line once OdysseusAgent is defined

async def run_odysseus(start_concept: Optional[str] = None, start_url: Optional[str] = None, max_iterations: int = 10):
    """
    Runs the Odysseus bot using the OpenAI Agents SDK.
    Requires either a start_concept (for initial search) or a start_url.
    """
    if not start_concept and not start_url:
        start_concept = input("What is the problem I should learn about? ")

    visited_urls: Set[str] = set()
    current_url: Optional[str] = start_url
    current_concept: Optional[str] = start_concept

    print(f"Starting Odysseus exploration. Max iterations: {max_iterations}")

    for i in range(max_iterations):
        print(f"\n--- Iteration {i + 1}/{max_iterations} ---")

        input_prompt = ""
        # Normalize URL before adding to visited set and using in prompt
        normalized_url = current_url.split('?')[0] if current_url else None

        if current_url:
            if normalized_url in visited_urls:
                print(f"URL already visited: {current_url}. Stopping this path.")
                # Simple strategy: switch to search based on the last concept if we hit a visited URL
                current_concept = f"Find related info; {current_url} was already visited."
                current_url = None # Force search in the next block
                # Alternatively, the agent could be prompted to handle the revisit
            else:
                print(f"Processing URL: {current_url}")
                visited_urls.add(normalized_url)
                # The agent needs a tool (e.g., WebReaderTool) to handle this URL
                input_prompt = f"Analyze the content of the URL: {current_url}. Visited URLs: {list(visited_urls)}"

        # This elif handles both the initial start and subsequent searches
        if not current_url and current_concept:
             print(f"Searching based on concept: {current_concept}")
             # The agent will use its search tool (e.g., WebSearchTool)
             input_prompt = f"Search for information about: '{current_concept}'. Visited URLs: {list(visited_urls)}"

        # If no URL and no concept, we can't proceed
        if not input_prompt:
             print("Error: No URL or concept to process.")
             break

        # Run the main agent
        try:
            print("Running Agent...")
            # You might pass visited_urls via context if tools need dynamic access:
            # result = await Runner.run(agent, input_prompt, context={"visited_urls": visited_urls})
            result = await Runner.run(agent, input_prompt)

            if not result.final_output:
                 print("Agent did not produce a final output.")
                 # Decide how to handle this - maybe retry or stop?
                 current_concept = f"Agent failed to produce output for previous step ({'URL: '+current_url if current_url else 'Concept: '+current_concept}). Try searching for related information."
                 current_url = None
                 continue # Try searching in the next iteration


            next_step = result.final_output_as(NextStep) # Agent must output this type

            print(f"Agent Reasoning: {next_step.reasoning}")

            # Update state for the next iteration
            current_url = next_step.next_url
            current_concept = next_step.search_query # If agent provides a new query

            # If agent provides neither, exploration stops
            if not current_url and not current_concept:
                print("Agent decided to stop or could not determine a valid next step.")
                break

        except Exception as e:
            print(f"An error occurred during agent execution: {e}")
            # Consider more specific error handling or retry logic
            print("Stopping exploration due to error.")
            break # Stop on error

        # Optional delay?
        # await asyncio.sleep(1)

    print("\n--- Odysseus Exploration Complete ---")
    print(f"Visited URLs ({len(visited_urls)}): {visited_urls}")


def main(**kwargs):
    # Fire needs a sync entry point, asyncio.run handles the async call
    asyncio.run(run_odysseus(**kwargs))

if __name__ == "__main__":
    # Allows running via `python odysseus.py --start_url="..."` or prompts for concept
    Fire(main)