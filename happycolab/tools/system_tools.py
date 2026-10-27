"""
Standard built-in system tools (Web browsing, search, time, calculator).
"""

import webbrowser
import datetime
import urllib.parse


def open_google(search_query: str = "") -> str:
    """
    Opens Google in the default web browser. If a search query is provided, searches for it.
    """
    if search_query:
        query_encoded = urllib.parse.quote(search_query)
        target = f"https://www.google.com/search?q={query_encoded}"
        webbrowser.open(target)
        return f"Opened Google search for '{search_query}' in your web browser."
    else:
        webbrowser.open("https://www.google.com")
        return "Opened Google in your web browser."


def open_url(url: str) -> str:
    """
    Opens any website URL in the user's default browser (e.g. 'https://github.com').
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened website: {url}"


def get_system_time() -> str:
    """
    Returns the current local date, time, and timezone on this machine.
    """
    now = datetime.datetime.now()
    return f"Current local time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


def calculate(expression: str) -> str:
    """
    Evaluates basic mathematical expressions like '25 * 4 + 10' safely.
    """
    allowed_chars = set("0123456789+-*/(). %")
    if not all(c in allowed_chars for c in expression):
        return "Error: Expression contains unsupported characters."
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"
