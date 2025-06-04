# FastAPI routes

from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.travel_agent import build_travel_agent

router = APIRouter()


class TripRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: str
    interests: list[str]
    budget: int


@router.post("/plan-trip")
async def plan_trip(request: TripRequest):
    agent = build_travel_agent()
    result = agent.invoke({
        "destination": request.destination,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "interests": request.interests,
        "budget": request.budget
    })
    return result
