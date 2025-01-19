from pydantic import BaseModel, field_validator
from datetime import datetime as dt
from datetime import timedelta as td


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


def main() -> None:
    try:
        order = Order(
            id=1,
            item_name="Laptop",
            quantity=0,
            order_date=dt.now(),
            delivery_date=dt.now(),
        )  # + td(days=7))

        print(order)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
