# 🌟 HappyColab (Python Library)

**HappyColab** is a high-speed Python client and AI agent framework that lets you run Large Language Models in **Google Colab** (with free GPU acceleration) and call them from any other machine with **native Tool & Function Calling**, real-time streaming, error recovery guides, and interactive chat.

---

## 📁 Repository Structure

```text
HappyColab/
├── happycolab/                 # 📦 Library Source Code
│   ├── __init__.py             # Exports HappyAgent, HappyClient, tool
│   ├── agent.py                # Agent with auto-schema tool decorator & loop
│   ├── client.py               # Low-level OpenAI-compatible API connector
│   ├── config.py               # Error recovery, guided troubleshooting & configs
│   ├── cli.py                  # CLI command runner (happycolab, happy-chat)
│   └── tools/                  # Built-in tool suite
│       ├── system_tools.py     # Open Google, open URL, calculate, local time
│       └── id_card_tools.py    # ID card verification & clearance checks
│
├── examples/                   # 💡 Ready-to-Run Examples
│   ├── 01_simple_chat.py       # Basic single-turn Q&A
│   ├── 02_streaming.py         # Real-time token streaming
│   ├── 03_custom_tool.py       # Adding a custom tool
│   ├── 04_full_assistant.py    # Interactive assistant with all default tools
│   └── 05_custom_function_calling.py # All 3 ways to register function calling
│
├── colab_server/               # 🚀 Laptop 1 (Colab Server Files)
│   ├── colab_server_code.py    # Copy-pasteable script for Google Colab
│   └── colab_server_notebook.ipynb # Ready-to-upload Colab notebook
│
├── .gitignore
├── pyproject.toml
├── setup.py
└── requirements.txt
```

---

## ⚡ Quick Start (2 Minutes)

### Step 1: Install HappyColab
```powershell
pip install happycolab
```

### Step 2: Launch Server on Google Colab (Free T4 GPU)
You can get the Colab notebook or code in any of these easy ways:

- **Export the Colab Notebook to your current folder**:
  ```powershell
  happycolab --notebook
  ```
  *(Then drag & drop `colab_server_notebook.ipynb` into [Google Colab](https://colab.research.google.com))*

- **Or Copy the Server Script directly to your clipboard**:
  ```powershell
  happycolab --copy
  ```
  *(Open Colab with T4 GPU, create a code cell, and press `Ctrl+V`!)*

- **Or view the setup code in terminal**:
  ```powershell
  happycolab --colab
  ```

Run all cells in Colab and copy the public Cloudflare URL (e.g. `https://xxxx.trycloudflare.com`).

### Step 3: Interactive Chat & Function Calling
Launch the interactive terminal chat:
```powershell
happycolab
```
*(Or alias: `happy-chat`)*

If your URL changes or expires, **HappyColab displays a step-by-step troubleshooting guide** and lets you paste your new URL directly into the prompt!

---

## 🛠️ Adding Function Calling (3 Ways)

Users can add custom functions for the LLM to call in any of these 3 ways:

### Method 1: Using `@agent.tool` Decorator
Type hints and docstrings are automatically converted into OpenAI function calling schemas:
```python
from happycolab import HappyAgent

agent = HappyAgent(url="https://your-url.trycloudflare.com")

@agent.tool
def get_user_profile(user_id: str) -> dict:
    """Fetch employee department and clearance by User ID."""
    return {"user_id": user_id, "name": "Jane Miller", "department": "AI Security"}
```

### Method 2: Using the Standalone `@tool` Decorator
```python
from happycolab import HappyAgent, tool

@tool
def calculate_tax(amount: float, tax_rate_percent: float = 10.0) -> dict:
    """Calculate tax and total cost for a transaction."""
    tax = amount * (tax_rate_percent / 100.0)
    return {"subtotal": amount, "tax": tax, "total": amount + tax}

agent = HappyAgent(url="https://your-url.trycloudflare.com")
agent.add_tool(calculate_tax)
```

### Method 3: Registering Regular Python Functions (No Decorators!)
```python
def check_server(server_name: str) -> dict:
    """Check health and ping of an internal server."""
    return {"server": server_name, "status": "ONLINE", "uptime": "99.9%"}

agent.add_tool(check_server)
# Or bulk register:
# agent.add_tools([func_a, func_b, func_c])
```

---

## ⚡ Real-Time Token Streaming

HappyColab streams responses token-by-token in both the CLI and Python scripts:

```python
from happycolab import HappyAgent

agent = HappyAgent(url="https://your-url.trycloudflare.com")

# Stream answer in real-time
for token in agent.stream_ask("Explain quantum computing in 3 sentences"):
    print(token, end="", flush=True)
```

---

## 📥 Dynamic Model Management from Local Machine

Download any model directly onto your Google Colab GPU right from your local machine:

### In Terminal Chat:
While chatting inside `happycolab`, you can use slash commands:
- `/pull llama3.2:3b` ➔ Download and load new model onto Colab GPU with a live progress bar!
- `/model llama3.2:3b` ➔ Switch model dynamically (prompts to download if missing).
- `/models` ➔ Query all models installed on Colab with disk sizes.
- `/delete <name>` ➔ Delete a model from Colab GPU to free memory.
- `/url <new_url>` ➔ Change the tunnel URL on the fly.
- `/tools` ➔ View active tools.
- `/help` ➔ Show troubleshooting guide.

### In Python:
```python
# Pull a new model onto Colab GPU
agent.pull_model("deepseek-r1:8b")

# Switch active model
agent.set_model("deepseek-r1:8b")

# List all models with details
print(agent.client.list_models_detailed())
```

