import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from happycolab import HappyAgent

COLAB_URL = "https://polished-hang-corrections-skip.trycloudflare.com"

# Initialize HappyAgent
agent = HappyAgent(url=COLAB_URL, model="qwen2.5:7b")

# Define a custom tool with the decorator!
@agent.tool
def generate_discount_coupon(customer_name: str, percent_off: int) -> dict:
    """Generate a custom discount promotional code for a customer."""
    code = f"SAVE{percent_off}-{customer_name[:3].upper()}99"
    return {"customer": customer_name, "coupon_code": code, "discount": f"{percent_off}%"}

# Ask question requiring the tool
print("Querying HappyAgent...")
result = agent.ask("Create a 20% discount coupon for Sarah Connor.")
print("\nAgent Answer:\n", result)
