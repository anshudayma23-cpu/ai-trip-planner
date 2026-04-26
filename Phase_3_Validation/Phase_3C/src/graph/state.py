from typing import TypedDict, Annotated
from operator import add

class TravelConstraints(TypedDict):
    destination_country: str
    cities: list[str]
    duration_days: int
    budget_usd: float
    preferences: list[str]   # e.g. ["food", "temples"]
    avoidances: list[str]    # e.g. ["crowds"]

class DayPlan(TypedDict):
    day: int
    city: str
    morning: str
    afternoon: str
    evening: str
    estimated_cost_usd: float

class AgentState(TypedDict):
    user_request: str
    constraints: TravelConstraints | None
    research_notes: Annotated[list[str], add]
    accommodation: list[dict]
    daily_plans: list[DayPlan]
    intercity_transport: list[dict]
    budget_report: dict | None
    qa_result: dict | None
    revision_count: int
    status: str  # "parsing" | "researching" | "planning" | "budgeting" | "reviewing" | "completed" | "failed"
    error: str | None
    final_itinerary: str | None
