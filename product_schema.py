# product_schema.py
from pydantic import BaseModel, Field
from typing import List

class ProductComparison(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    price: float = Field(..., description="Price of the product in USD")
    battery_life: str = Field(..., description="Battery life description, e.g., '10 hours'")
    pros_summary: List[str] = Field(..., description="List of summarized positive points")
    cons_summary: List[str] = Field(..., description="List of summarized negative points")