# # ==============================================================================
# # GOOGLE COLAB LLM SERVER (RUN THIS IN GOOGLE COLAB ON LAPTOP 1)
# # ==============================================================================
# # Instructions:
# # 1. Open a new notebook at https://colab.research.google.com
# # 2. Go to Runtime -> Change runtime type -> Select T4 GPU (Free tier)
# # 3. Create a code cell, paste the code below, and run it.
# # 4. It will install Ollama & Cloudflare, pull Qwen 2.5 (great for chat + tool calling),
# #    and print a public URL (e.g., https://xxxx.trycloudflare.com).
# # 5. Copy that URL and use it in your client script on Laptop 2!
# # ==============================================================================

# # Cell 1: Install Ollama & Cloudflare Tunnel
# !apt-get update -qq && apt-get install -y -qq zstd
# !curl -fsSL https://ollama.com/install.sh | sh
# !wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
# !dpkg -i cloudflared-linux-amd64.deb

# # Cell 2: Start Ollama daemon & pull model
# import os
# import subprocess
# import time
# import re
# import sys

# # Configure Ollama to accept all external origins and hosts
# os.environ["OLLAMA_HOST"] = "0.0.0.0:11434"
# os.environ["OLLAMA_ORIGINS"] = "*"

# print("[1/3] Starting Ollama server...")
# ollama_proc = subprocess.Popen(["ollama", "serve"])
# time.sleep(4)

# # Pull Qwen 2.5 7B (State of the art open model with exceptional function calling capability)
# # Tip: If you want a smaller/faster model on T4 GPU, you can use "qwen2.5:3b" or "llama3.2:3b"
# MODEL_NAME = "qwen2.5:7b"
# print(f"[2/3] Downloading model '{MODEL_NAME}' (takes ~1-2 mins)...")
# subprocess.run(["ollama", "pull", MODEL_NAME], check=True)

# # Cell 3: Launch Cloudflare Tunnel and display public URL
# print("[3/3] Exposing server to internet via Cloudflare Tunnel...")
# # Note: --http-host-header localhost rewrites the Host header to avoid 403 Forbidden
# tunnel_proc = subprocess.Popen(
#     ["cloudflared", "tunnel", "--url", "http://127.0.0.1:11434", "--http-host-header", "localhost:11434"],
#     stdout=subprocess.PIPE,
#     stderr=subprocess.PIPE,
#     text=True
# )

# public_url = None
# for line in tunnel_proc.stderr:
#     match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
#     if match:
#         public_url = match.group(0)
#         break

# if public_url:
#     print("\n" + "=" * 65)
#     print("🚀 SUCCESS! YOUR COLAB LLM SERVER IS LIVE!")
#     print(f"👉 PUBLIC URL: {public_url}")
#     print(f"👉 API BASE URL FOR CLIENT: {public_url}/v1")
#     print(f"👉 MODEL NAME: {MODEL_NAME}")
#     print("=" * 65 + "\n")
#     print("Keep this Colab tab running while testing from your other laptop.")
# else:
#     print("Failed to get Cloudflare tunnel URL automatically. Check tunnel_proc output.")

# # Keep running
# tunnel_proc.wait()
