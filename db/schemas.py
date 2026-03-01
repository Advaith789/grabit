from pydantic import BaseModel, Field
from typing import Optional


class FoodItem(BaseModel):
    name: str = Field(description="Main name of the food item")
    cuisine: Optional[str] = Field(
        description="The cuisine of the dish. Null if unknown."
    )
    quantity: Optional[str] = Field(
        description="The quantity of the food. Null if unknown."
    )


class ExtractionResult(BaseModel):
    foods: list[FoodItem] = Field(description="List of extracted food items")
    email_body: str = Field(
        description="A friendly, concise email message for the user."
    )
    email_subject: str = Field(
        description="An exciting, short subject line for the email."
    )
