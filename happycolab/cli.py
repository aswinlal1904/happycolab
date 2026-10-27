"""
Command-line interface entry point for happycolab and happy-chat.
Provides guided error recovery, interactive link pasting, and model switching.
"""

import argparse
import sys
from .agent import HappyAgent
from .config import load_config, save_config, print_error_guide
from .notebook import (
    export_notebook,
    copy_colab_script,
    open_colab,
    COLAB_SERVER_SCRIPT,
)

DEFAULT_FALLBACK_URL = "https://varieties-investors-agreements-patients.trycloudflare.com"
DEFAULT_FALLBACK_MODEL = "qwen2.5:7b"


def main():
    cfg = load_config()
    saved_url = cfg.get("url", DEFAULT_FALLBACK_URL)
    saved_model = cfg.get("model", DEFAULT_FALLBACK_MODEL)

    parser = argparse.ArgumentParser(
        description="HappyColab: High-speed LLM client with local tool execution backed by Google Colab"
    )
    parser.add_argument("--url", default=saved_url, help=f"Cloudflare URL from Colab (default: {saved_url})")
    parser.add_argument("--model", default=saved_model, help=f"Model name (default: {saved_model})")
    parser.add_argument("--no-tools", action="store_true", help="Disable default local tools")
    parser.add_argument(
        "--notebook",
        nargs="?",
        const="colab_server_notebook.ipynb",
        metavar="FILENAME",
        help="Export the ready-to-run Colab server notebook into the current directory",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy the Google Colab server script directly to your clipboard",
    )
    parser.add_argument(
        "--open-colab",
        action="store_true",
        help="Open Google Colab directly in your web browser",
    )
    parser.add_argument(
        "--colab",
        action="store_true",
        help="Print the Google Colab server setup code in the terminal",
    )
    args = parser.parse_args()

    # Handle utility flags
    if args.notebook:
        out_file = export_notebook(args.notebook)
        print("\n" + "=" * 65)
        print("🎉 GOOGLE COLAB NOTEBOOK EXPORTED!")
        print(f"📁 Saved to: {out_file}")
        print("\nNext steps:")
        print("  1. Go to https://colab.research.google.com")
        print("  2. Click 'Upload' and select this file")
        print("  3. Set Runtime to T4 GPU and run all cells!")
        print("=" * 65 + "\n")
        return

    if args.copy:
        copied = copy_colab_script()
        print("\n" + "=" * 65)
        if copied:
            print("📋 Colab server script copied to your clipboard!")
            print("👉 Open Google Colab (T4 GPU), create a cell, and press Ctrl+V to paste!")
        else:
            print("Could not copy directly to clipboard on this system.")
            print("Use 'happycolab --colab' to print the full script here.")
        print("=" * 65 + "\n")
        return

    if args.open_colab:
        print("Opening Google Colab in your browser...")
        open_colab()
        return

    if args.colab:
        print("\n" + "=" * 70)
        print("🚀 GOOGLE COLAB SERVER SETUP CODE")
        print("=" * 70)
        print(COLAB_SERVER_SCRIPT)
        return

    active_url = args.url
    active_model = args.model

    agent = HappyAgent(url=active_url, model=active_model)

    # Verify connection
    print(f"\n🔍 Connecting to HappyColab LLM at: {active_url} (Model: {active_model}) ...")
    connected, reason = agent.client.ping_detailed()
    if connected:
        save_config(url=active_url, model=active_model)

    while not connected:
        # Show guided troubleshooting steps
        print_error_guide(active_url, reason)

        user_input = input("👉 Paste your active Colab Cloudflare URL (or press Enter to exit): ").strip()
        if not user_input:
            print("\nExiting. Start your Colab notebook and run happycolab again anytime.")
            sys.exit(0)

        active_url = user_input
        agent.set_url(active_url)
        print(f"\nRetrying connection to: {active_url} ...")
        connected, reason = agent.client.ping_detailed()

        if connected:
            save_config(url=active_url)
            print(" Connected successfully!")
            break

    if not args.no_tools:
        agent.load_default_tools()

    agent.interactive_chat()


if __name__ == "__main__":
    main()
