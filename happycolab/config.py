"""
Configuration and troubleshooting helper for HappyColab.
Manages persistent URLs, model preferences, and helpful error guidance.
"""

import json
import os
from typing import Dict, Any, Optional

CONFIG_FILE_NAME = ".happycolab.json"


def get_config_path() -> str:
    """Returns local project config path, or user home directory path."""
    cwd_path = os.path.join(os.getcwd(), CONFIG_FILE_NAME)
    if os.path.exists(cwd_path):
        return cwd_path
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, CONFIG_FILE_NAME)


def load_config() -> Dict[str, Any]:
    """Loads saved config if exists."""
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(url: Optional[str] = None, model: Optional[str] = None):
    """Saves preferences to config file."""
    cfg = load_config()
    if url:
        cfg["url"] = url
    if model:
        cfg["model"] = model
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def print_error_guide(url: str, reason: str = ""):
    """
    Displays a friendly, clear troubleshooting guide when connection fails.
    """
    print("\n" + "═" * 70)
    print("⚠️   COULD NOT CONNECT TO GOOGLE COLAB LLM")
    print("═" * 70)
    if reason:
        print(f"👉 Error Details: {reason}")
    print(f"👉 Target URL   : {url}")
    print("\n📋 STEP-BY-STEP TROUBLESHOOTING GUIDE:")
    print("  1. Check Colab on Laptop 1:")
    print("     Make sure your Google Colab tab is open and the notebook cell is actively running.")
    print("  2. Cloudflare URLs are temporary:")
    print("     Every time you restart Colab or restart the tunnel, a NEW .trycloudflare.com")
    print("     URL is created. The previous link expires immediately.")
    print("  3. Check for 403 Forbidden:")
    print("     If you see a 403 error, ensure your Colab cell has:")
    print("       os.environ['OLLAMA_ORIGINS'] = '*'")
    print("       and cloudflared is run with: --http-host-header localhost:11434")
    print("  4. Check GPU & Model:")
    print("     In Colab, go to Runtime -> Change runtime type -> Ensure T4 GPU is selected.")
    print("  5. Need the Server Script or Notebook?")
    print("     Run 'happycolab --notebook' to export the Colab notebook to this folder,")
    print("     or 'happycolab --copy' to copy the server code directly to your clipboard!")
    print("═" * 70 + "\n")
