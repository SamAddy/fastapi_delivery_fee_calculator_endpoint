from datetime import datetime

from pydantic import BaseModel, Field


class DeliveryFeeRequest(BaseModel):
    """
    Represents the request payload for calculating the delivery fee.

    Attributes:
        cart_value (int): Total value of items in the shopping cart.
            Constraints:
                - Greater than 0.

        delivery_distance (int): The distance for the delivery.
            Constraints:
                - Greater than 0.

        number_of_items (int): The total number of items in the shopping cart.
            Constraints:
                - Greater than 0.

        time (datetime): Order time in UTC in ISO format.
            Default: Current time in ISO format (datetime.now().isoformat()).
    """
    cart_value: int = Field(gt=0, description="number_of_items cannot be less than 1")
    delivery_distance: int = Field(gt=0, description="number_of_items cannot be less than 1")
    number_of_items: int = Field(gt=0, description="number_of_items cannot be less than 1")
    time: datetime = Field(default=datetime.now().isoformat(),
                           description="Order time in UTC in ISO format")


class DeliveryFeeResponse(BaseModel):
    """
    Represents the response payload for the calculated delivery fee.

    Attributes:
        delivery_fee (int): Calculated delivery fee for the given request.
    """
    delivery_fee: int = Field(..., description="Calculated delivery fee")
