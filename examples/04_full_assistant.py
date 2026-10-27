"""
HappyColab: Full interactive assistant with built-in tools:
- Opens Google / Web browser on this machine
- Looks up ID cards and verifies clearance
- Calculates math
- Reports local system time
- Full conversational memory
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from happycolab import HappyAgent

COLAB_URL = "https://polished-hang-corrections-skip.trycloudflare.com"

# Create agent
agent = HappyAgent(url=COLAB_URL, model="qwen2.5:7b")

# Load all built-in system and ID card tools
agent.load_default_tools()

# Launch interactive while True chat loop
if __name__ == "__main__":
    agent.interactive_chat()
