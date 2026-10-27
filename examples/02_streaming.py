import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from happycolab import HappyAgent

COLAB_URL = "https://varieties-investors-agreements-patients.trycloudflare.com"

agent = HappyAgent(url=COLAB_URL, model="qwen2.5:7b")

print("Streaming token-by-token response with agent.stream_ask():\n")
for token in agent.stream_ask("Explain quantum computing in 3 short sentences."):
    print(token, end="", flush=True)
print()
