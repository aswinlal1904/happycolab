"""
Example 05: All ways to add Function Calling / Tools in HappyColab.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from happycolab import HappyAgent, tool

COLAB_URL = "https://polished-hang-corrections-skip.trycloudflare.com"

# 1. Initialize Agent
agent = HappyAgent(url=COLAB_URL, model="qwen2.5:7b")


# Method 1: Using the @agent.tool decorator
@agent.tool
def get_user_profile(user_id: str) -> dict:
    """Fetch employee department and clearance by User ID."""
    return {"user_id": user_id, "name": "Jane Miller", "department": "AI Security", "clearance": "Level 5"}


# Method 2: Using standalone @tool decorator
@tool
def calculate_tax(amount: float, tax_rate_percent: float = 10.0) -> dict:
    """Calculate tax and total cost for a transaction."""
    tax = amount * (tax_rate_percent / 100.0)
    return {"subtotal": amount, "tax": tax, "total": amount + tax}

agent.add_tool(calculate_tax)


# Method 3: Registering a regular Python function directly (no decorator needed!)
def get_server_status(server_name: str) -> dict:
    """Check health and ping of an internal server."""
    return {"server": server_name, "status": "ONLINE", "uptime": "99.98%", "latency_ms": 12}

agent.add_tool(get_server_status)


# Test the tools:
if __name__ == "__main__":
    print("Testing Method 1 (User profile)...")
    ans1 = agent.ask("Look up profile for user ID-8800")
    print("Answer:\n", ans1)

    print("\nTesting Method 2 (Calculate tax)...")
    ans2 = agent.ask("What is the tax on $450 with 8% rate?")
    print("Answer:\n", ans2)
