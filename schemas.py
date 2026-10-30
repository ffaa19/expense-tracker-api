
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime




class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    description: str = Field(min_length=1)
    date: date

    @field_validator("category", "description")
    @classmethod
    def validate_non_empty_strings(cls, value):
        if not value.strip():
            raise ValueError("This field cannot be empty")
        return value.strip()




class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    description: str
    date: date
    created_at: datetime
