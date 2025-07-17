
from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from code.llm import get_llm
from code.paths import CONFIG_FILE_PATH
from code.utils import load_config

config = load_config(CONFIG_FILE_PATH)

# Our Product model
class Product(BaseModel):
    name: str = Field("The name of the product.")
    price: float = Field("The product's price.")
    features: List[str] = Field("Product's features.")
    category: str = Field("Product category. One of [Beverages, Dairy, Grocery]")

class ProductListingAI:
    def __init__(self):
        llm = get_llm(config.get("llm", "gpt-4o-mini"))
        self.model = llm
        self.prompt = ChatPromptTemplate.from_template(
            "Generate product information for: {description}"
        )
        self.chain = self.prompt | self.model.with_structured_output(Product)

    def generate_product_listing(self, description: str) -> dict | BaseModel:
        """Generate structured product listing from description."""
        return self.chain.invoke({"description": description})