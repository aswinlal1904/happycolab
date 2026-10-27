"""
HappyColab: A Python library for running LLMs in Google Colab and executing tools locally on your client machine.
"""

from .client import HappyClient, ColabClient
from .agent import HappyAgent, ColabAgent, tool
from .tools import ALL_DEFAULT_TOOLS
from .notebook import (
    export_notebook,
    copy_colab_script,
    open_colab,
    COLAB_SERVER_SCRIPT,
)

__version__ = "1.1.0"
__all__ = [
    "HappyClient",
    "HappyAgent",
    "ColabClient",
    "ColabAgent",
    "tool",
    "ALL_DEFAULT_TOOLS",
    "export_notebook",
    "copy_colab_script",
    "open_colab",
    "COLAB_SERVER_SCRIPT",
]
