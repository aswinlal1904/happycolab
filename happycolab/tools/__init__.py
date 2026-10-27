"""
Built-in tools bundle for colab-llm.
"""

from .system_tools import open_google, open_url, get_system_time, calculate
from .id_card_tools import lookup_id_card, verify_security_clearance

ALL_DEFAULT_TOOLS = [
    open_google,
    open_url,
    get_system_time,
    calculate,
    lookup_id_card,
    verify_security_clearance,
]

__all__ = [
    "open_google",
    "open_url",
    "get_system_time",
    "calculate",
    "lookup_id_card",
    "verify_security_clearance",
    "ALL_DEFAULT_TOOLS",
]
