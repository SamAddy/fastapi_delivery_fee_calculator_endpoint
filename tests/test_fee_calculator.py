from datetime import datetime

import pytest
from pydantic import ValidationError

from delivery_fee_calculator.fee_calculator import CalculateDeliveryFee
from delivery_fee_calculator.schemas import DeliveryFeeRequest
from tests.test_data import negative_values_cart, zero_values_cart, maximum_fee_limit_cart, minimum_values_cart, \
    zero_fee_cart, normal_cart, invalid_cart


@pytest.fixture
def delivery_fee_calculator():
    return CalculateDeliveryFee()


def test_calculate_cart_value_surcharge_thresholds(delivery_fee_calculator):
    assert delivery_fee_calculator.calculate_cart_value_surcharge(8.9) == 1.1
    assert delivery_fee_calculator.calculate_cart_value_surcharge(10) == 0
    assert delivery_fee_calculator.calculate_cart_value_surcharge(15) == 0
    assert delivery_fee_calculator.calculate_cart_value_surcharge(0.01) == 10


def test_calculate_distance_fee_below_threshold(delivery_fee_calculator):
    # Test that distance below the threshold (1000 meters) has fee = 2
    assert delivery_fee_calculator.calculate_distance_fee(999) == 2


def test_calculate_distance_fee_threshold(delivery_fee_calculator):
    assert delivery_fee_calculator.calculate_distance_fee(1000) == 2


def test_calculate_distance_fee_above_threshold(delivery_fee_calculator):
    # Test that distance above the threshold (1000 meters) gets + 1
    # based on the number of 500m intervals
    assert delivery_fee_calculator.calculate_distance_fee(1499) == 3
    assert delivery_fee_calculator.calculate_distance_fee(1500) == 3
    assert delivery_fee_calculator.calculate_distance_fee(1501) == 4
    assert delivery_fee_calculator.calculate_distance_fee(2235) == 5


def test_calculate_items_surcharge_no_surcharge_condition(delivery_fee_calculator):
    # Test when num_of_items is less than 4 return 0
    assert delivery_fee_calculator.calculate_items_surcharge(4) == 0


def test_calculate_items_surcharge_above_threshold(delivery_fee_calculator):
    # Test if number_of_items is greater than 4 and cart_value > 10:
    # surcharge = ((number_of_items-4) * 0.5) + 1.2 if number_of_items > 12
    assert delivery_fee_calculator.calculate_items_surcharge(5) == 0.5
    assert delivery_fee_calculator.calculate_items_surcharge(10) == 3
    assert delivery_fee_calculator.calculate_items_surcharge(13) == 5.7
    assert delivery_fee_calculator.calculate_items_surcharge(14) == 6.2


def test_calculate_rush_hour_fee_rush_hour_time(delivery_fee_calculator):
    # Test rush hour time - should return 1.2
    rush_hour_time = datetime.fromisoformat("2024-01-19T15:33:00Z")
    assert delivery_fee_calculator.calculate_rush_hour_fee(rush_hour_time) == 1.2


def test_calculate_rush_hour_fee_rush_day_but_not_in_rush_hour(delivery_fee_calculator):
    # Test rush day but not in rush hour - should return 1
    rush_hour_time = datetime.fromisoformat("2024-01-19T13:33:00Z")
    assert delivery_fee_calculator.calculate_rush_hour_fee(rush_hour_time) == 1


def test_calculate_rush_hour_fee_non_rush_hour_time(delivery_fee_calculator):
    # Test non-rush hour time - should return 1
    non_rush_hour_time = datetime.fromisoformat("2024-01-15T13:00:00Z")
    assert delivery_fee_calculator.calculate_rush_hour_fee(non_rush_hour_time) == 1


def test_calculate_rush_hour_fee_invalid_data_type_common_string_input(delivery_fee_calculator):
    # Test invalid data type - should return 1
    invalid_data_type = "invalid_data_type"
    assert delivery_fee_calculator.calculate_rush_hour_fee(invalid_data_type) == 1


def test_calculate_rush_hour_fee_invalid_iso_format(delivery_fee_calculator):
    with pytest.raises(ValueError, match=".*Invalid isoformat string: *."):
        invalid_iso_format = datetime.fromisoformat("invalid_iso_format")
        delivery_fee_calculator.calculate_rush_hour_fee(invalid_iso_format)


def test_calculate_delivery_fee(delivery_fee_calculator):
    cart = DeliveryFeeRequest(**normal_cart)
    assert delivery_fee_calculator.calculate_delivery_fee(request_data=cart) == 710


def test_calculate_delivery_fee_no_charge_for_large_cart(delivery_fee_calculator):
    # Test when cart value is greater than or equal to 200, there should be no delivery charge
    cart = DeliveryFeeRequest(**zero_fee_cart)

    calculated_fee = delivery_fee_calculator.calculate_delivery_fee(request_data=cart)
    assert calculated_fee == 0


def test_calculate_delivery_fee_minimum_values(delivery_fee_calculator):
    # Test with the minimum values for each parameter, expecting a non-zero fee
    cart = DeliveryFeeRequest(**minimum_values_cart)
    calculated_fee = delivery_fee_calculator.calculate_delivery_fee(request_data=cart)
    assert calculated_fee > 0


def test_calculate_delivery_fee_maximum_fee_limit(delivery_fee_calculator):
    # Test when the calculated fee exceeds the maximum delivery fee, it should be capped at the maximum
    cart = DeliveryFeeRequest(**maximum_fee_limit_cart)

    calculated_fee = delivery_fee_calculator.calculate_delivery_fee(request_data=cart)
    # Convert the calculated fee to cent
    assert calculated_fee == delivery_fee_calculator.MAXIMUM_DELIVERY_FEE * 100


def test_calculate_delivery_fee_zero_values(delivery_fee_calculator):
    with pytest.raises(ValidationError) as exc_info:
        DeliveryFeeRequest(**zero_values_cart)

    # Ensure that each field's validation error is present in the exception message
    assert "cart_value" in str(exc_info.value)
    assert "delivery_distance" in str(exc_info.value)
    assert "number_of_items" in str(exc_info.value)


def test_calculate_delivery_fee_negative_values(delivery_fee_calculator):
    with pytest.raises(ValidationError) as exc_info:
        DeliveryFeeRequest(**negative_values_cart)

    assert "cart_value" in str(exc_info.value)
    assert "delivery_distance" in str(exc_info.value)
    assert "number_of_items" in str(exc_info.value)


def test_calculate_delivery_fee_invalid_data_types(delivery_fee_calculator):
    with pytest.raises(ValidationError) as exc_info:
        DeliveryFeeRequest(**invalid_cart)

    assert "cart_value" in str(exc_info.value)
    assert "delivery_distance" in str(exc_info.value)
    assert "number_of_items" in str(exc_info.value)
    assert "time" in str(exc_info.value)
