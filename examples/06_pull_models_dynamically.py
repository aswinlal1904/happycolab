"""
Example 06: Downloading and Managing Models on Google Colab GPU Dynamically
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from happycolab import HappyAgent

# Replace with your active Cloudflare tunnel URL from Colab
COLAB_URL = "https://varieties-investors-agreements-patients.trycloudflare.com"

agent = HappyAgent(url=COLAB_URL)

print("1. Querying models currently installed on Colab GPU:")
models = agent.client.list_models_detailed()
for m in models:
    size_mb = m.get("size", 0) // (1024 * 1024)
    print(f"  • {m.get('name'):<20} ({size_mb} MB)")

# Download a lightweight model directly onto Colab GPU with progress bar
target_model = "qwen2.5:0.5b"
print(f"\n2. Downloading '{target_model}' to Google Colab GPU:")
agent.pull_model(target_model)

print("\n3. Testing streaming completion with newly pulled model:")
for token in agent.stream_ask("Give me 3 tips for learning AI in 1 bullet each."):
    print(token, end="", flush=True)
print()
