from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from delivery_fee_calculator.fee_calculator import CalculateDeliveryFee
from delivery_fee_calculator.main import app
from tests.test_data import normal_cart, invalid_cart, maximum_fee_limit_cart

client = TestClient(app)

calculator = CalculateDeliveryFee()


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to API Playground" in response.content


def test_calculate_delivery_fee_endpoint():
    response = client.post("/fees", json=normal_cart)
    assert response.status_code == 201
    assert response.json() == {"delivery_fee": 710}


def test_calculate_delivery_fee_with_invalid_data():
    calculator.calculate_delivery_fee = MagicMock()
    response = client.post("/fees", json=invalid_cart)
    assert response.status_code == 422
    assert "detail" in response.json()

    assert isinstance(response.json()["detail"], list)

    for error_entry in response.json()["detail"]:
        assert "type" in error_entry
        assert "loc" in error_entry
        assert "msg" in error_entry

    calculator.calculate_delivery_fee.assert_not_called()


def test_maximum_delivery_fee():
    response = client.post("/fees", json=maximum_fee_limit_cart)
    assert response.status_code == 201
    assert response.json() == {"delivery_fee": 1500}
