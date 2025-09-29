from pydantic import BaseModel, HttpUrl
from typing import Optional

class Product(BaseModel):
    product_name: str
    price: float
    link: HttpUrl