#!/usr/bin/env python
"""
Main entry point for the Odysseus agent.

This file provides backward compatibility with the original implementation
and delegates to the new refactored modules.
"""

import os
from dotenv import load_dotenv
from fire import Fire

from odysseus.agent import OdysseusAgent
from odysseus_cli import run_odysseus

# This file is kept for backward compatibility
# The actual implementation has been moved to:
# - odysseus/agent.py: OdysseusAgent class
# - tools/url_utils.py: URL normalization functions
# - odysseus_cli.py: Command-line interface

if __name__ == "__main__":
    Fire(run_odysseus) 