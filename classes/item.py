from decimal import Decimal, getcontext
from pydantic import BaseModel, field_validator

class Item(BaseModel):
    """Class representing an item in the warehouse.
    
    Specifies name, quantity, unit of measure, and unit price.
    
    Specifies methods to convert numeric fields to Decimal type,

    Instatiate with keyword arguments `name`, `quantity`, `unit`, `unit_price` due to Pydantic BaseModel.
    """
    name : str
    quantity : Decimal
    unit : str
    unit_price : Decimal

    def __repr__(self):
        return (
            f"Item(name={self.name!r}, "
            f"quantity={self.quantity!r}, "
            f"unit={self.unit!r}, "
            f"unit_price={self.unit_price!r})"
        )
    
    @field_validator("quantity", "unit_price", mode="before")
    def ensure_decimal(cls, v):
        """Ensure the field passed to initializer is converted exactly to Decimal."""
        if isinstance(v, float):
            return Decimal(str(v), context=getcontext())  # exact conversion
        return Decimal(v)
