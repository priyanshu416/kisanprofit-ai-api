from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4

app = FastAPI(title="KisanProfit AI API", version="0.1.0",
              description="One backend API for KisanProfit AI demo features.")

# Demo CORS: restrict this to your frontend domain before production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CropRequest(BaseModel):
    state: str = "Punjab"
    soil_type: str = "Loamy"
    water: str = "Reliable irrigation"

class ProfitRequest(BaseModel):
    acres: float = Field(ge=0)
    yield_per_acre: float = Field(ge=0, description="Quintals per acre")
    price_per_quintal: float = Field(ge=0)
    cost_per_acre: float = Field(ge=0)

class BenefitCreate(BaseModel):
    scheme: str
    status: str = "Considering"
    note: Optional[str] = ""

class BenefitUpdate(BaseModel):
    status: str

# Temporary in-memory demo storage. Data is lost when the server restarts.
benefits = {}

@app.get("/")
def root():
    return {"name": "KisanProfit AI API", "version": "0.1.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/recommend-crops")
def recommend_crops(req: CropRequest):
    if req.water.lower() == "rain-fed":
        crops = ["Millet", "Pulses", "Maize"]
    elif req.soil_type.lower() == "clay":
        crops = ["Rice", "Wheat", "Mustard"]
    else:
        crops = ["Wheat", "Maize", "Pulses"]
    return {
        "state": req.state,
        "suggestions": crops,
        "demo": True,
        "notice": "Illustrative only. Verify season, soil test, local weather, and market conditions."
    }

@app.post("/calculate-profit")
def calculate_profit(req: ProfitRequest):
    revenue = req.acres * req.yield_per_acre * req.price_per_quintal
    costs = req.acres * req.cost_per_acre
    return {
        "revenue": round(revenue, 2),
        "costs": round(costs, 2),
        "net_profit": round(revenue - costs, 2),
        "currency": "INR"
    }

@app.post("/diagnose")
def diagnose():
    return {
        "status": "model_not_connected",
        "message": "API route is ready, but a trained crop disease model has not been connected yet."
    }

@app.get("/mandi-prices")
def mandi_prices(state: str = "Punjab", crop: Optional[str] = None):
    sample = [
        {"crop": "Wheat", "price_per_quintal": 2275, "trend": "stable"},
        {"crop": "Rice", "price_per_quintal": 2300, "trend": "up"},
        {"crop": "Maize", "price_per_quintal": 2050, "trend": "stable"},
    ]
    if crop:
        sample = [x for x in sample if x["crop"].lower() == crop.lower()]
    return {"state": state, "data": sample, "demo": True,
            "notice": "Sample values only; not live mandi prices."}

@app.get("/schemes")
def schemes():
    return [
        {"name": "PM-KISAN", "url": "https://pmkisan.gov.in/"},
        {"name": "Kisan Credit Card", "url": "https://fasalrin.gov.in/"},
        {"name": "PM Fasal Bima Yojana", "url": "https://pmfby.gov.in/"},
        {"name": "myScheme", "url": "https://www.myscheme.gov.in/"},
    ]

@app.get("/benefits")
def list_benefits():
    return list(benefits.values())

@app.post("/benefits", status_code=201)
def create_benefit(req: BenefitCreate):
    item = {"id": str(uuid4()), **req.model_dump()}
    benefits[item["id"]] = item
    return item

@app.patch("/benefits/{benefit_id}")
def update_benefit(benefit_id: str, req: BenefitUpdate):
    if benefit_id not in benefits:
        return {"error": "Benefit entry not found"}
    benefits[benefit_id]["status"] = req.status
    return benefits[benefit_id]

@app.delete("/benefits/{benefit_id}")
def delete_benefit(benefit_id: str):
    if benefit_id not in benefits:
        return {"error": "Benefit entry not found"}
    del benefits[benefit_id]
    return {"deleted": True}
