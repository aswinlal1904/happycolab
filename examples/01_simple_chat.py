import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from happycolab import HappyClient

COLAB_URL = "https://polished-hang-corrections-skip.trycloudflare.com"

client = HappyClient(url=COLAB_URL, model="qwen2.5:7b")

reply = client.chat([
    {"role": "user", "content": "Explain machine learning in 2 short bullet points."}
])

print("Reply from HappyColab LLM:\n", reply)
