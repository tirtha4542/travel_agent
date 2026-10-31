from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., description="User travel query or prompt", min_length=1)
    thread_id: Optional[str] = Field(None, description="Optional thread ID for conversational memory persistence")
    user_location: Optional[str] = Field(None, description="Detected or preferred user origin location (e.g. 'Dhaka, Bangladesh')")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Markdown formatted travel response")
    thread_id: str = Field(..., description="Thread session ID used for memory checkpoints")
    user_location: Optional[str] = Field(None, description="User location context used in planning")
    flight_results: Optional[str] = Field("", description="Raw or formatted flight data")
    hotel_results: Optional[str] = Field("", description="Raw or formatted hotel search data")
    itinerary: Optional[str] = Field("", description="Draft itinerary text")
    llm_calls: Optional[int] = Field(0, description="Total number of LLM invocations in this run")
