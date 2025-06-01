"""field validator"""

from datetime import datetime as dt
from datetime import timedelta as td

from pydantic import BaseModel, field_validator


class Order(BaseModel):
    id: int
    item_name: str
    quantity: int
    order_date: dt
    delivery_date: dt

    @field_validator("quantity")
    def validate_quantity(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Quantity must be greater than 0")
        return value

    @field_validator("delivery_date")
    def validate_delivery_date(cls, value: dt) -> dt:
        if value < dt.now():
            raise ValueError("Delivery date must be in the future")
        return value

    def __str__(self) -> str:
        return (
            f"Order(id={self.id}, item_name={self.item_name}, quantity={self.quantity}, "
            f"order_date={self.order_date.__format__('%Y-%m-%d %H:%M:%S')}, delivery_date={self.delivery_date.date()})"
        )


# Entrypoint
def main() -> None:
    # Field validator success
    try:
        order = Order(
            id=1,
            item_name="Laptop",
            quantity=1,
            order_date=dt.now(),
            delivery_date=dt.now() + td(days=3),
        )
        print(f"\nField validator success: \n{order}")

    except ValueError as e:
        print(f"\nField validator error: \n{e}")

    # Field validator error
    try:
        order = Order(
            id=1,
            item_name="Laptop",
            quantity=0,
            order_date=dt.now(),
            delivery_date=dt.now() - td(days=3),
        )
        print(f"\nField validator success: \n{order}")

    except ValueError as e:
        print(f"\nField validator error: \n{e}")


if __name__ == "__main__":
    main()
