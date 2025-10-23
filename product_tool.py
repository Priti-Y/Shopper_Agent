# product_tool.py
import json
from langchain.tools import StructuredTool, Tool
from pydantic import BaseModel, Field
from product_schema import ProductComparison
from typing import List

# Input model for the tool
class ProductInput(BaseModel):
    product_name: str
    price: float
    battery_life: str
    pros_summary: List[str]
    cons_summary: List[str]

# Function to create structured product data
def create_product_comparison(
    product_name: str,
    price: float,
    battery_life: str,
    pros_summary: List[str],
    cons_summary: List[str]
) -> ProductComparison:
    return ProductComparison(
        product_name=product_name,
        price=price,
        battery_life=battery_life,
        pros_summary=pros_summary,
        cons_summary=cons_summary
    )

# Wrap as a LangChain StructuredTool
# Keep a programmatic function for direct calls
product_comparison_tool = create_product_comparison

# Also provide a StructuredTool for structured/call-site usage (not for ZeroShotAgent)
structured_product_comparison_tool = StructuredTool.from_function(
    func=create_product_comparison,
    name="structured_product_comparison_tool",
    description="Creates structured product comparison data",
    args_schema=ProductInput,
)

# Agent-compatible wrapper: ZeroShotAgent requires single-string input tools.
def _agent_wrapper(input_str: str) -> str:
    """Accept a JSON string describing the product fields, create the ProductComparison,
    and return a JSON string. This keeps the tool single-input and agent-friendly.
    """
    try:
        data = json.loads(input_str)
    except Exception:
        return json.dumps({"error": "Invalid input. Provide a JSON string with keys: product_name, price, battery_life, pros_summary, cons_summary"})

    try:
        pc = create_product_comparison(**data)
        return pc.json()
    except Exception as e:
        return json.dumps({"error": str(e)})

# Tool instance suitable for ZeroShotAgent (single string input)
product_comparison_agent_tool = Tool(
    name="product_comparison_tool",
    func=_agent_wrapper,
    description="Create a product comparison from a JSON string input and return JSON."
)
