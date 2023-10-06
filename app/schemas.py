from pydantic import BaseModel, constr, conint, validator
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class Category(BaseModel):
    id: int
    name: str

class InventoryItemResponse(BaseModel):

    id: int
    name: str
    description: str
    quantity: int
    price: float
    created_at: datetime
    updated_at: datetime
    category: Category
    low_stock_threshold: int
    status: Optional[str]

class SaleQueryParams(BaseModel):
    start_date: date
    end_date: date
    item_id: conint(ge=1) = None  
    category_id: conint(ge=1) = None
    interval: constr() = "daily"

    @validator("end_date")
    def validate_end_date(cls, value, values):
        if value < values.get("start_date"):
            raise ValueError("end_date cannot be earlier than start_date")
        return value
    

class InventoryCreateItem(BaseModel):
    name: str
    description: str
    quantity: int
    price: float
    low_stock_threshold: int
    category_id: int