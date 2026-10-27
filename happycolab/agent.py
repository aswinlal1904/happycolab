"""
ColabAgent: High-level Agent class with automatic tool schema generation,
execution dispatch, and conversational memory.
"""

import inspect
import json
from typing import Callable, Dict, Any, List, Optional, Generator
from .client import HappyClient


def python_type_to_json_type(py_type: Any) -> str:
    """Map python types to JSON schema types."""
    if py_type in (int,):
        return "integer"
    if py_type in (float,):
        return "number"
    if py_type in (bool,):
        return "boolean"
    if py_type in (list, List):
        return "array"
    if py_type in (dict, Dict):
        return "object"
    return "string"


def generate_tool_schema(func: Callable) -> Dict[str, Any]:
    """
    Automatically converts a Python function and its docstring/type hints
    into an OpenAI-compatible function calling schema.
    """
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or f"Execute {func.__name__}"

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
        json_type = python_type_to_json_type(param_type)

        properties[name] = {
            "type": json_type,
            "description": f"Parameter '{name}'",
        }

        if param.default == inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": doc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def tool(func: Callable) -> Callable:
    """
    Standalone decorator to mark a Python function as a tool.
    Usage:
        @tool
        def my_func(query: str) -> str:
            '''Look up information.'''
            return "data"

        agent.add_tool(my_func)
    """
    func.__is_happy_tool__ = True
    func.__tool_schema__ = generate_tool_schema(func)
    return func


class HappyAgent:
    """
    Intelligent Agent running against a Colab-hosted LLM with local tool execution.
    """

    def __init__(
        self,
        url: str,
        model: str = "qwen2.5:7b",
        system_prompt: Optional[str] = None,
        timeout: float = 90.0,
    ):
        self.client = HappyClient(url=url, model=model, timeout=timeout)
        self.model = model
        self.system_prompt = system_prompt or (
            "You are a helpful and intelligent AI assistant. "
            "You have access to tools that can be executed on the user's local machine. "
            "When the user requests an action (such as opening a website or checking records), "
            "use the relevant tool. Always provide friendly, direct answers."
        )
        self.tools_registry: Dict[str, Callable] = {}
        self.tools_schema: List[Dict[str, Any]] = []
        self.history: List[Dict[str, Any]] = [{"role": "system", "content": self.system_prompt}]

    def tool(self, func: Callable) -> Callable:
        """
        Decorator to register a Python function as a tool on this agent instance.
        Example:
            @agent.tool
            def open_google() -> str:
                '''Opens Google in the web browser.'''
                import webbrowser
                webbrowser.open("https://www.google.com")
                return "Google opened successfully"
        """
        self.add_tool(func)
        return func

    def add_tool(self, func: Callable, schema: Optional[Dict[str, Any]] = None):
        """
        Register a single function as an executable tool.
        If no custom schema is provided, auto-generates schema from docstring and type hints.
        """
        self.tools_registry[func.__name__] = func
        auto_schema = schema or getattr(func, "__tool_schema__", None) or generate_tool_schema(func)

        # Replace existing schema if updating, or append
        existing_idx = next((i for i, s in enumerate(self.tools_schema) if s.get("function", {}).get("name") == func.__name__), None)
        if existing_idx is not None:
            self.tools_schema[existing_idx] = auto_schema
        else:
            self.tools_schema.append(auto_schema)

    def add_tools(self, funcs: List[Callable]):
        """
        Bulk register multiple functions as tools.
        Example:
            agent.add_tools([fetch_weather, calculate_tax, open_dashboard])
        """
        for f in funcs:
            self.add_tool(f)

    # Aliases
    register_tool = add_tool
    register_tools = add_tools

    def load_default_tools(self):
        """Load all built-in tools (Google, URLs, Time, Calculator, ID Card lookup)."""
        from .tools import ALL_DEFAULT_TOOLS
        for t in ALL_DEFAULT_TOOLS:
            if t.__name__ not in self.tools_registry:
                self.add_tool(t)

    def set_model(self, model: str):
        """Change the active model name."""
        self.model = model.strip()
        self.client.set_model(self.model)

    def set_url(self, url: str):
        """Update the active Colab URL."""
        self.client.set_url(url)

    def list_models(self) -> List[str]:
        """List models available on the Colab server."""
        return self.client.list_models()

    def ping(self) -> bool:
        """Verify server connection."""
        return self.client.ping()

    def reset_history(self):
        """Clear conversation history."""
        self.history = [{"role": "system", "content": self.system_prompt}]

    def ask(self, user_query: str, verbose: bool = True) -> str:
        """
        Process a user input, execute tools if requested by the LLM, and return response.
        """
        self.history.append({"role": "user", "content": user_query})

        # Request completion from Colab LLM
        if self.tools_schema:
            response_msg = self.client.chat_with_tools(
                messages=self.history,
                tools=self.tools_schema,
            )
        else:
            raw_reply = self.client.chat(messages=self.history)
            self.history.append({"role": "assistant", "content": raw_reply})
            return raw_reply

        # Handle tool execution loop
        if response_msg.tool_calls:
            self.history.append(response_msg)

            for tool_call in response_msg.tool_calls:
                func_name = tool_call.function.name
                func_args_str = tool_call.function.arguments or "{}"
                try:
                    func_args = json.loads(func_args_str)
                except Exception:
                    func_args = {}

                call_id = tool_call.id

                if verbose:
                    print(f"  ⚡ [Tool Executing] {func_name}({func_args})")

                # Dispatch locally
                if func_name in self.tools_registry:
                    try:
                        res = self.tools_registry[func_name](**func_args)
                        output_str = json.dumps(res) if not isinstance(res, str) else res
                    except Exception as err:
                        output_str = json.dumps({"error": str(err)})
                else:
                    output_str = json.dumps({"error": f"Tool '{func_name}' is not registered."})

                if verbose:
                    print(f"  👉 [Result] {output_str}")

                self.history.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": output_str,
                })

            # Get final formulated reply with tool results
            final_reply = self.client.chat(messages=self.history)
            self.history.append({"role": "assistant", "content": final_reply})
            return final_reply
        else:
            reply = response_msg.content or ""
            self.history.append({"role": "assistant", "content": reply})
            return reply

    def stream_ask(self, user_query: str, verbose: bool = True) -> Generator[str, None, None]:
        """
        Process user query with real-time streaming tokens and automatic local tool execution.
        """
        self.history.append({"role": "user", "content": user_query})

        if self.tools_schema:
            response_msg = self.client.chat_with_tools(
                messages=self.history,
                tools=self.tools_schema,
            )

            if response_msg.tool_calls:
                self.history.append(response_msg)

                for tool_call in response_msg.tool_calls:
                    func_name = tool_call.function.name
                    func_args_str = tool_call.function.arguments or "{}"
                    try:
                        func_args = json.loads(func_args_str)
                    except Exception:
                        func_args = {}

                    call_id = tool_call.id

                    if verbose:
                        print(f"  ⚡ [Tool Executing] {func_name}({func_args})")

                    if func_name in self.tools_registry:
                        try:
                            res = self.tools_registry[func_name](**func_args)
                            output_str = json.dumps(res) if not isinstance(res, str) else res
                        except Exception as err:
                            output_str = json.dumps({"error": str(err)})
                    else:
                        output_str = json.dumps({"error": f"Tool '{func_name}' is not registered."})

                    if verbose:
                        print(f"  👉 [Result] {output_str}")

                    self.history.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": output_str,
                    })

                # Stream final formulated reply with tool results
                full_reply = ""
                for chunk in self.client.stream_chat(messages=self.history):
                    full_reply += chunk
                    yield chunk
                self.history.append({"role": "assistant", "content": full_reply})
                return
            else:
                reply = response_msg.content or ""
                self.history.append({"role": "assistant", "content": reply})
                yield reply
                return
        else:
            full_reply = ""
            for chunk in self.client.stream_chat(messages=self.history):
                full_reply += chunk
                yield chunk
            self.history.append({"role": "assistant", "content": full_reply})
            return

    def pull_model(self, model_name: str, verbose: bool = True) -> bool:
        """
        Download a new model onto Google Colab GPU with a live progress bar.
        Automatically sets active model to the new model on completion.
        """
        import sys
        from .config import save_config

        model_name = model_name.strip()
        if verbose:
            print(f"\n📥 Requesting Google Colab to download '{model_name}'...")

        last_status = ""
        try:
            for progress in self.client.pull_model(model_name):
                status = progress.get("status", "")
                completed = progress.get("completed", 0)
                total = progress.get("total", 0)

                if total > 0:
                    pct = (completed / total) * 100
                    mb_completed = completed / (1024 * 1024)
                    mb_total = total / (1024 * 1024)
                    bar_len = 25
                    filled = int(bar_len * (completed / total))
                    bar = "█" * filled + "░" * (bar_len - filled)
                    sys.stdout.write(f"\r  [{bar}] {pct:5.1f}% ({mb_completed:6.1f} MB / {mb_total:6.1f} MB) {status[:22]}")
                    sys.stdout.flush()
                else:
                    if status and status != last_status:
                        sys.stdout.write(f"\n  ℹ️  {status}")
                        sys.stdout.flush()
                        last_status = status

            print(f"\n✅ Successfully pulled and loaded '{model_name}' onto Google Colab GPU!")
            self.set_model(model_name)
            save_config(model=model_name)
            return True
        except Exception as e:
            print(f"\n❌ Failed to pull model '{model_name}': {e}")
            return False

    def delete_model(self, model_name: str) -> bool:
        """Delete a model from Google Colab GPU to free memory."""
        ok = self.client.delete_model(model_name)
        if ok:
            print(f"🗑️ Model '{model_name}' deleted from Colab.")
        else:
            print(f"❌ Failed to delete model '{model_name}'.")
        return ok

    # Aliases
    chat = ask
    __call__ = ask

    def interactive_chat(self):
        """Launch interactive terminal chat session with commands and error guidance."""
        from .config import print_error_guide, save_config

        print("\n" + "=" * 65)
        print("🤖 HAPPYCOLAB AGENT - INTERACTIVE CHAT")
        print(f"   Model       : {self.model}")
        print(f"   Endpoint    : {self.client.url}")
        print(f"   Tools Active: {list(self.tools_registry.keys()) or 'None'}")
        print("\n💡 Commands:")
        print("   /pull <model>  -> Download new model onto Colab GPU (e.g. /pull llama3.2:3b)")
        print("   /model <name>  -> Switch active model")
        print("   /models        -> List models on Colab with sizes")
        print("   /delete <name> -> Delete model from Colab GPU")
        print("   /url <link>    -> Change Colab Cloudflare URL")
        print("   /tools         -> Show active tools")
        print("   /clear         -> Reset conversation history")
        print("   /help          -> Show troubleshooting guide")
        print("   exit / quit    -> End chat")
        print("=" * 65)

        while True:
            try:
                user_msg = input("\nYou: ").strip()
                if not user_msg:
                    continue

                # Exit command
                if user_msg.lower() in ("exit", "quit", "q"):
                    print("Goodbye!")
                    break

                # Help command
                if user_msg.lower() == "/help":
                    print_error_guide(self.client.url, "User requested /help guide.")
                    continue

                # Clear history
                if user_msg.lower() == "/clear":
                    self.reset_history()
                    print("🧹 Conversation history cleared.")
                    continue

                # Show active tools
                if user_msg.lower() == "/tools":
                    print(f"\nRegistered Tools ({len(self.tools_registry)}):")
                    for t_name, t_func in self.tools_registry.items():
                        print(f"  • {t_name}: {inspect.getdoc(t_func) or 'No docstring'}")
                    continue

                # Pull model command
                if user_msg.lower().startswith("/pull"):
                    parts = user_msg.split(maxsplit=1)
                    if len(parts) > 1:
                        target = parts[1].strip()
                        self.pull_model(target)
                    else:
                        target = input("Enter model to pull (e.g. llama3.2:3b, deepseek-r1:8b, mistral:7b): ").strip()
                        if target:
                            self.pull_model(target)
                    continue

                # Delete model command
                if user_msg.lower().startswith("/delete"):
                    parts = user_msg.split(maxsplit=1)
                    if len(parts) > 1:
                        target = parts[1].strip()
                        self.delete_model(target)
                    else:
                        target = input("Enter model to delete from Colab: ").strip()
                        if target:
                            self.delete_model(target)
                    continue

                # List models on Colab
                if user_msg.lower() == "/models":
                    print("Fetching models from Colab...")
                    detailed = self.client.list_models_detailed()
                    if detailed:
                        print("\nInstalled Models on Colab:")
                        for m in detailed:
                            m_name = m.get("name", "")
                            size_bytes = m.get("size", 0)
                            size_gb = size_bytes / (1024 * 1024 * 1024)
                            marker = " (Active)" if m_name == self.model or m_name.startswith(self.model) else ""
                            print(f"  • {m_name:<22} [{size_gb:4.1f} GB]{marker}")
                    else:
                        avail_models = self.list_models()
                        if avail_models:
                            print("Installed Models on Colab:")
                            for m in avail_models:
                                marker = " (Active)" if m == self.model else ""
                                print(f"  • {m}{marker}")
                        else:
                            print(f"Current model is: {self.model}.")
                    continue

                # Change model command
                if user_msg.lower().startswith("/model"):
                    parts = user_msg.split(maxsplit=1)
                    if len(parts) > 1:
                        new_model = parts[1].strip()
                    else:
                        print(f"Current model: '{self.model}'")
                        new_model = input("Enter new model name (e.g. qwen2.5:7b, llama3.2:3b, mistral:7b): ").strip()

                    if new_model:
                        avail = self.list_models()
                        if avail and not any(m == new_model or m.startswith(new_model) for m in avail):
                            confirm = input(f"Model '{new_model}' is not installed on Colab. Download it now? (y/n): ").strip().lower()
                            if confirm in ("y", "yes"):
                                if self.pull_model(new_model):
                                    continue
                        self.set_model(new_model)
                        save_config(model=new_model)
                        print(f"✅ Model switched to: '{new_model}'")
                    continue

                # Change URL command
                if user_msg.lower().startswith("/url"):
                    parts = user_msg.split(maxsplit=1)
                    if len(parts) > 1:
                        new_url = parts[1].strip()
                    else:
                        new_url = input("Enter new Colab Cloudflare URL: ").strip()

                    if new_url:
                        self.set_url(new_url)
                        ok, msg = self.client.ping_detailed()
                        if ok:
                            save_config(url=new_url)
                            print(f"✅ URL updated & verified: {new_url}")
                        else:
                            print_error_guide(new_url, msg)
                    continue

                # Real-time token streaming chat
                print(f"\n🤖 HappyColab LLM:")
                for token in self.stream_ask(user_msg, verbose=True):
                    print(token, end="", flush=True)
                print()

            except KeyboardInterrupt:
                print("\nSession paused.")
                break
            except Exception as e:
                err_msg = str(e)
                print(f"\n❌ Error encountered: {err_msg}")
                # Print guided walkthrough
                print_error_guide(self.client.url, err_msg)

                # Offer immediate prompt to paste a new URL or model
                prompt_fix = input("Paste your new Colab URL here (or press Enter to retry / skip): ").strip()
                if prompt_fix:
                    if prompt_fix.startswith("http"):
                        self.set_url(prompt_fix)
                        ok, msg = self.client.ping_detailed()
                        if ok:
                            save_config(url=prompt_fix)
                            print(f"🎉 Successfully reconnected to: {prompt_fix}")
                        else:
                            print(f"⚠️ Still unable to connect: {msg}")
                    else:
                        print("Invalid URL format. Expected 'https://...trycloudflare.com'")


# Backward compatibility alias
ColabAgent = HappyAgent

