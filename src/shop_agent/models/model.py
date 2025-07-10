from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Budget(BaseModel):
    min: Optional[float] = Field(None, description="Minimum budget")
    max: Optional[float] = Field(None, description="Maximum budget")


class UserPreference(BaseModel):
    item: str = Field(..., description="The name of the product or item")
    brand: Optional[List[str]] = Field(None, description="Preferred brand(s), if mentioned")
    preferred_colors: Optional[List[str]] = Field(None, description="Preferred color(s), if mentioned")
    budget: Optional[Budget] = Field(None, description="Budget range if specified")
    features: Optional[List[str]] = Field(None, description="Key product features the user mentioned")

    class Config:
        schema_extra = {
            "example": {
                "item": "earbuds",
                "brand": ["boAt"],
                "preferred_colors": ["black"],
                "budget": {"min": None, "max": 1500},
                "features": ["wireless", "noise cancellation"]
            }
        }

class ExtractedProductNames(BaseModel):
    items: List[str] = Field(
        ...,
        description="A list of product names extracted from the markdown file"
    )

