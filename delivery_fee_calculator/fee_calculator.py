from calendar import day_name
from datetime import datetime
from math import ceil

from delivery_fee_calculator.schemas import DeliveryFeeRequest


class CalculateDeliveryFee:
    """A class to calculate delivery fees based on various factors."""

    def __init__(self):
        self.BASE_FEE = 2
        self.ADDITIONAL_FEE = 1
        self.CART_VALUE_WITH_SURCHARGE = 10
        self.BASE_SURCHARGE = 0.50
        self.NUMBER_OF_ITEMS_WITHOUT_SURCHARGE = 4
        self.EXTRA_FEE_THRESHOLD = 12
        self.EXTRA_FEE = 1.20
        self.RUSH_HOUR_FEE_MULTIPLIER = 1.2
        self.RUSH_DAY = "Friday"
        self.MAXIMUM_DELIVERY_FEE = 15
        self.DISTANCE_THRESHOLD_1 = 1000
        self.DISTANCE_THRESHOLD_2 = 500
        self.RUSH_HOUR_RANGE_IN_SECONDS = range(54000, 68400)
        self.CART_VALUE_WITH_NO_DELIVERY_FEE = 200

    def calculate_cart_value_surcharge(self, cart_value: float) -> float:
        """
        Calculate the surcharge based on the cart value.

        Args:
            cart_value (float): The total value of items in the cart (in EUR).

        Returns:
            float: The calculated surcharge in EUR.

        Example:
            >>> calculator = CalculateDeliveryFee()
            >>> calculator.calculate_cart_value_surcharge(8.9)
            1.1
        """
        surcharge = 0

        if cart_value < self.CART_VALUE_WITH_SURCHARGE:
            surcharge += self.CART_VALUE_WITH_SURCHARGE - cart_value

        return round(surcharge, 1)

    def calculate_distance_fee(self, distance: int) -> int:
        """
            Calculate the distance fee.

            Args:
                distance (int): The delivery distance in meters.

            Returns:
                int: The calculated delivery fee in EUR.

            Example:
                >>> calculator = CalculateDeliveryFee()
                >>> calculator.calculate_distance_fee(1499)
                3
        """
        if distance <= self.DISTANCE_THRESHOLD_1:
            return self.BASE_FEE

        additional_distance = distance - self.DISTANCE_THRESHOLD_1

        if additional_distance <= self.DISTANCE_THRESHOLD_2:
            return self.BASE_FEE + self.ADDITIONAL_FEE

        additional_distance_interval = ceil(additional_distance / self.DISTANCE_THRESHOLD_2)

        return self.BASE_FEE + self.ADDITIONAL_FEE * additional_distance_interval

    def calculate_items_surcharge(self, number_of_items: int) -> float:
        """
        Calculate surcharge based on the number of items.

        Args:
            number_of_items (int): The number of items in the cart.

        Returns:
            float: The calculated surcharge in EUR.

        Example:
            >>> calculator = CalculateDeliveryFee()
            >>> calculator.calculate_items_surcharge(3)
            0
        """
        surcharge = 0

        if number_of_items <= self.NUMBER_OF_ITEMS_WITHOUT_SURCHARGE:
            return surcharge

        surcharge += ((number_of_items - self.NUMBER_OF_ITEMS_WITHOUT_SURCHARGE)
                      * self.BASE_SURCHARGE)
        extra_fee = 0 if number_of_items <= self.EXTRA_FEE_THRESHOLD else self.EXTRA_FEE

        return round(surcharge + extra_fee, 1)

    def calculate_rush_hour_fee(self, datetime_: datetime) -> float:
        """
        Calculate the rush hour fee based on the specified date and time.

        Args:
            datetime_ (datetime): The datetime object representing the delivery time.

        Returns:
            float: The rush hour fee multiplier.

        Example:
            >>> calculator = CalculateDeliveryFee()
            >>> calculator.calculate_rush_hour_fee(datetime.fromisoformat("2024-01-19T15:33:00Z"))
            1.2
        """
        if not isinstance(datetime_, datetime):
            return 1

        weekday = day_name[datetime_.weekday()]
        time_ = datetime_.time()
        seconds = (time_.hour * 60 + time_.minute) * 60 + time_.second

        if weekday == self.RUSH_DAY and seconds in self.RUSH_HOUR_RANGE_IN_SECONDS:
            return self.RUSH_HOUR_FEE_MULTIPLIER
        return 1

    def calculate_delivery_fee(self, request_data: DeliveryFeeRequest) -> int:
        """
        Calculate the total delivery fee based on the request data.

        Args:
            request_data (DeliveryFeeRequest): An object containing delivery request data.

        Returns:
            int: The total calculated delivery fee in cents.

        Example:
            >>> calculator = CalculateDeliveryFee()
            >>> request = DeliveryFeeRequest(cart_value=790, delivery_distance=2235,
            number_of_items=4, time="2024-01-15T15:33:00Z")
            >>> calculator.calculate_delivery_fee(request)
            910
        """
        total_fees = 0
        request_data.cart_value /= 100  # convert cents to eur

        if request_data.cart_value >= self.CART_VALUE_WITH_NO_DELIVERY_FEE:
            return total_fees

        total_fees += self.calculate_cart_value_surcharge(request_data.cart_value)
        total_fees += self.calculate_distance_fee(request_data.delivery_distance)
        total_fees += self.calculate_items_surcharge(request_data.number_of_items)

        datetime_ = datetime.fromisoformat(str(request_data.time))
        total_fees *= self.calculate_rush_hour_fee(datetime_)

        total_fees = min(total_fees, self.MAXIMUM_DELIVERY_FEE)
        total_fees_to_cents = round(total_fees * 100)
        return total_fees_to_cents
