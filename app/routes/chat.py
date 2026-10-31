import logging
from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.graph import run_travel_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/health")
async def health_check():
    """Health check endpoint to verify backend status."""
    return {"status": "healthy", "service": "TreapMate AI Travel Planner"}


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Processes a user travel query through the LangGraph multi-agent workflow with location awareness."""
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    try:
        # Run synchronous LangGraph agent in FastAPI worker threadpool
        result = await run_in_threadpool(
            run_travel_agent,
            user_query=request.message.strip(),
            thread_id=request.thread_id,
            user_location=request.user_location.strip() if request.user_location else None
        )

        return ChatResponse(
            answer=result.get("answer", "No response generated."),
            thread_id=result.get("thread_id", ""),
            user_location=result.get("user_location", request.user_location),
            flight_results=result.get("flight_results", ""),
            hotel_results=result.get("hotel_results", ""),
            itinerary=result.get("itinerary", ""),
            llm_calls=result.get("llm_calls", 0),
        )
    except Exception as e:
        logger.error(f"Error during agent execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Travel agent execution failed: {str(e)}"
        )
