from fastapi import FastAPI, status

from delivery_fee_calculator.fee_calculator import CalculateDeliveryFee
from delivery_fee_calculator.schemas import DeliveryFeeRequest, DeliveryFeeResponse

calculator = CalculateDeliveryFee()

tags_metadata = [
    {
        "name": "fees",
        "description": ""
    }
]

app = FastAPI(
    title="Delivery Fee Calculator",
    summary="Calculate delivery fee",
    version="0.01",
    contact={
        "name": "SamAddy",
        "url": "https://samaddy.github.io/",
    }
)


@app.post("/fees", tags=["fees"], status_code=status.HTTP_201_CREATED)
async def calculate_delivery_fee(request_data: DeliveryFeeRequest) -> DeliveryFeeResponse:
    calculated_fee = calculator.calculate_delivery_fee(request_data)
    return DeliveryFeeResponse(delivery_fee=calculated_fee)
