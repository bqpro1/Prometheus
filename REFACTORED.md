# Odysseus: Autonomous Web Explorer Agent

This project has been refactored to use the OpenAI Agents SDK, providing better structure, reliability, and extensibility. The agent system can autonomously explore the web, read content, and build knowledge over time.

## Key Changes

1. **Adoption of OpenAI Agents SDK**
   - Structured agent architecture with tools and standardized interactions
   - Enhanced tracing capabilities for monitoring and debugging
   - Improved error handling and response validation

2. **Use of Docling for Web Content Extraction**
   - Better content extraction with fallback mechanisms
   - Cleaner text processing and structure preservation

3. **Modular Tool Architecture**
   - Brave Search integration for web search
   - Webpage content parser and link extractor
   - PDF parser for scientific papers

4. **Memory System**
   - Improved storage and retrieval of agent memories
   - Structured markdown format for storing reflections

## Setup and Usage

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure API keys in `.env` file:
   ```
   OPENAI_API_KEY=your-openai-api-key
   BRAVE_API_KEY=your-brave-search-api-key  
   ```

3. Run the agent:
   ```
   python odysseus_agent.py "concept to explore"
   ```

## Project Structure

- `odysseus_agent.py` - Main entry point and agent orchestration
- `tools/` - Custom tools for the agent
  - `brave_search.py` - Brave Search integration
  - `webpage_parser.py` - Web content extraction tools
  - `pdf_parser.py` - PDF processing tool
- `memory/` - Memory management system
- `prompts/` - System prompts defining agent behavior

## Workflow

The agent follows a cyclic pattern:

1. Search for information using Brave Search
2. Read and analyze webpage content using Docling
3. Create memory from the content
4. Decide to follow a link or perform a new search
5. Repeat from step 1 or 2 depending on the decision 