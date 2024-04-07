from fastapi import FastAPI, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/fees", tags=["fees"], status_code=status.HTTP_201_CREATED)
async def calculate_delivery_fee(request_data: DeliveryFeeRequest) -> DeliveryFeeResponse:
    calculated_fee = calculator.calculate_delivery_fee(request_data)
    return DeliveryFeeResponse(delivery_fee=calculated_fee)
