"""
Core API client for connecting to LLMs hosted on Google Colab or remote endpoints.
"""

from typing import List, Dict, Any, Generator, Optional
from openai import OpenAI


class HappyClient:
    """
    Connects to an OpenAI-compatible LLM server running in Google Colab via Cloudflare/ngrok.
    """

    def __init__(self, url: str, model: str = "qwen2.5:7b", timeout: float = 90.0):
        self.timeout = timeout
        self.model = model
        self.set_url(url)

    def set_url(self, url: str):
        """Update Colab tunnel URL and reconfigure OpenAI client."""
        raw_url = url.strip().rstrip("/")
        if raw_url.endswith("/v1"):
            self.root_url = raw_url[:-3]
            self.url = raw_url
        else:
            self.root_url = raw_url
            self.url = f"{raw_url}/v1"
        self.client = OpenAI(base_url=self.url, api_key="ollama", timeout=self.timeout)

    def set_model(self, model: str):
        """Update model name (e.g. 'qwen2.5:7b', 'llama3.2:3b', 'mistral:7b')."""
        self.model = model.strip()

    def ping(self) -> bool:
        """Check if Colab server is reachable and active."""
        ok, _ = self.ping_detailed()
        return ok

    def ping_detailed(self) -> tuple:
        """
        Check connection and return (success: bool, message: str).
        """
        try:
            models = self.client.models.list()
            return True, f"Connected! Found {len(models.data)} model(s) available."
        except Exception as e:
            err_str = str(e)
            if "403" in err_str:
                return False, "HTTP 403 Forbidden: Colab blocked the connection. Ensure OLLAMA_ORIGINS='*' and --http-host-header are configured in Colab."
            if "Connection refused" in err_str or "Failed to connect" in err_str or "ConnectError" in err_str:
                return False, "Connection Refused: Colab cell might not be running or Cloudflare tunnel is offline."
            return False, f"Connection Failed: {err_str}"

    def list_models(self) -> List[str]:
        """List model names available on the Colab server."""
        try:
            res = self.client.models.list()
            return [m.id for m in res.data]
        except Exception:
            return []

    def list_models_detailed(self) -> List[Dict[str, Any]]:
        """Query Ollama /api/tags for model details (size, format, family)."""
        import requests
        try:
            res = requests.get(f"{self.root_url}/api/tags", timeout=15.0)
            if res.status_code == 200:
                return res.json().get("models", [])
        except Exception:
            pass
        return []

    def pull_model(self, model_name: str) -> Generator[Dict[str, Any], None, None]:
        """
        Pull a new model onto Google Colab GPU.
        Yields streaming progress dictionaries: {"status": ..., "completed": ..., "total": ...}
        """
        import requests
        import json

        endpoint = f"{self.root_url}/api/pull"
        response = requests.post(
            endpoint,
            json={"name": model_name.strip(), "stream": True},
            stream=True,
            timeout=600.0,
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    yield data
                except Exception:
                    continue

    def delete_model(self, model_name: str) -> bool:
        """Delete a model from Google Colab GPU to free memory."""
        import requests
        endpoint = f"{self.root_url}/api/delete"
        try:
            res = requests.delete(endpoint, json={"name": model_name.strip()}, timeout=30.0)
            return res.status_code == 200
        except Exception:
            return False

    def chat(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Standard chat completion."""
        res = self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return res.choices[0].message.content or ""

    def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Generator[str, None, None]:
        """Stream response tokens in real-time."""
        stream = self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_choice: str = "auto",
        temperature: float = 0.2,
    ):
        """Invoke completion with tool definitions."""
        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
        )
        return res.choices[0].message


# Backward compatibility alias
ColabClient = HappyClient
