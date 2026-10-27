"""
Notebook and Google Colab utilities for HappyColab.
Allows users to export the ready-to-run Colab server notebook, copy the setup
script to their clipboard, or launch Google Colab directly in their browser.
"""

import os
import shutil
import subprocess
import sys
import webbrowser
from typing import Optional

COLAB_SERVER_SCRIPT = r"""# ==============================================================================
# GOOGLE COLAB LLM SERVER (RUN ON LAPTOP 1 IN GOOGLE COLAB)
# 1. Open Google Colab (Runtime -> Change runtime type -> T4 GPU)
# 2. Run the following code cells:
# ==============================================================================

# [1] Install Dependencies, Ollama and Cloudflare Tunnel
!apt-get update -qq && apt-get install -y -qq zstd
!curl -fsSL https://ollama.com/install.sh | sh
!wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
!dpkg -i cloudflared-linux-amd64.deb

# [2] Start Ollama server & Download Model
import os, subprocess, time
os.environ["OLLAMA_HOST"] = "0.0.0.0:11434"
os.environ["OLLAMA_ORIGINS"] = "*"
subprocess.Popen(["ollama", "serve"])
time.sleep(4)
MODEL = "qwen2.5:7b"
!ollama pull $MODEL

# [3] Launch Cloudflare Tunnel and Print Public Endpoint
import subprocess, re
tunnel_proc = subprocess.Popen(
    ["cloudflared", "tunnel", "--url", "http://127.0.0.1:11434", "--http-host-header", "localhost:11434"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
for line in tunnel_proc.stderr:
    match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
    if match:
        print("\n" + "=" * 60)
        print("🎉 YOUR COLAB LLM IS LIVE!")
        print(f"👉 COPY THIS URL TO YOUR LOCAL MACHINE: {match.group(0)}")
        print("=" * 60)
        break
tunnel_proc.wait()
"""


def get_bundled_notebook_path() -> str:
    """Returns the absolute path to the bundled colab_server_notebook.ipynb."""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    notebook_path = os.path.join(package_dir, "colab_server_notebook.ipynb")
    return notebook_path


def export_notebook(destination_path: Optional[str] = None) -> str:
    """
    Exports the bundled ready-to-run Google Colab notebook to the user's
    current working directory or a specified path.
    """
    src = get_bundled_notebook_path()
    if not os.path.exists(src):
        # Fallback to parent directory search if in developer editable mode
        parent_colab = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "colab_server", "colab_server_notebook.ipynb"))
        if os.path.exists(parent_colab):
            src = parent_colab
        else:
            raise FileNotFoundError(f"Could not locate bundled colab_server_notebook.ipynb at {src}")

    if destination_path is None:
        destination_path = os.path.join(os.getcwd(), "colab_server_notebook.ipynb")

    shutil.copyfile(src, destination_path)
    return os.path.abspath(destination_path)


def copy_to_clipboard(text: str) -> bool:
    """
    Copies text to system clipboard across Windows, macOS, and Linux without extra dependencies.
    """
    try:
        if sys.platform == "win32":
            subprocess.run(["clip"], input=text.encode("utf-16le"), check=True)
            return True
        elif sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            return True
        else:
            # Try xclip or wl-copy
            for cmd in [["xclip", "-selection", "clipboard"], ["wl-copy"], ["xsel", "--clipboard", "--input"]]:
                try:
                    subprocess.run(cmd, input=text.encode("utf-8"), check=True)
                    return True
                except (FileNotFoundError, subprocess.SubprocessError):
                    continue
            return False
    except Exception:
        return False


def copy_colab_script() -> bool:
    """Copies the 3-step Google Colab server code to clipboard."""
    return copy_to_clipboard(COLAB_SERVER_SCRIPT)


def open_colab():
    """Opens Google Colab in default web browser."""
    webbrowser.open("https://colab.research.google.com/#create=true")
