"""Root entry point for the packing assistant backend"""

import uuid
import fastapi
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from backend.agents.packing_agent import PackingAgent

app = fastapi.FastAPI()

master_agent = PackingAgent()

class CreatePlanRequest(BaseModel):
    """Model for the initial travel plan request."""
    origin_city: str
    destination: str
    start_date: str = Field(..., examples=["2025-10-15"])
    end_date: str = Field(..., examples=["2025-10-22"])
    adults: int = Field(..., gt=0)
    budget: int = Field(..., gt=0)
    foodie: bool = False
    entertainment: bool = False
    business: bool = False
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the chat thread")


class ChatRequest(BaseModel):
    """Model for a follow-up chat message."""
    thread_id: str
    user_input: str

class CreatePlanResponse(BaseModel):
    """Response model for the itinerary creation."""
    thread_id: str
    itinerary: str

class ChatResponse(BaseModel):
    """Response model for the chat interaction."""
    ai_message: str

@app.post("/plan/create", response_model=CreatePlanResponse)
async def create_itinerary(request: CreatePlanRequest) -> CreatePlanResponse:
    """
    Creates a new travel itinerary for the user

    Args:
        request (CreatePlanRequest): The request containing travel details.

    Returns:
        CreatePlanResponse: The response containing the thread ID and generated itinerary.

    Raises:
        HTTPException: If the AI fails to generate an itinerary or if invalid details are provided.
    """
    try:
        config = {"configurable": {"thread_id": request.thread_id}}

        initial_data = request.model_dump()
        initial_data["initial_plan_complete"] = False
        initial_data["messages"] = []

        response = await master_agent.graph.ainvoke(initial_data, config=config)

        itinerary = response["messages"][-1].content if response.get("messages") else None

        if not itinerary:
            raise fastapi.exceptions.HTTPException(status_code=500, detail="AI failed to generate an itinerary.")

        return CreatePlanResponse(thread_id=request.thread_id, itinerary=itinerary)

    except Exception as e:
        print(f"Error in /plan/create: {e}")
        raise fastapi.exceptions.HTTPException(status_code=400, detail="Invalid details provided or an error occurred.")

@app.post("/plan/chat", response_model=ChatResponse)
async def chat_with_master_agent(request: ChatRequest) -> ChatResponse:
    """
    Handles follow-up chat messages with the master agent

    Args:
        request (ChatRequest): The request containing the thread ID and user input.

    Returns:
        ChatResponse: The AI's response to the user's input

    Raises:
        HTTPException: If the thread ID is missing or if the AI fails to generate a response.
    """
    try:
        config = {"configurable": {"thread_id": request.thread_id}}

        response = await master_agent.graph.ainvoke(
            {"messages": [HumanMessage(content=request.user_input)]},
            config=config
        )

        messages = response.get("messages", [])
        if not messages or not hasattr(messages[-1], 'content'):
            raise fastapi.exceptions.HTTPException(status_code=500, detail="AI failed to generate a valid response.")

        return ChatResponse(ai_message=messages[-1].content)

    except Exception as e:
        print(f"Error in /plan/chat: {e}")
        raise fastapi.exceptions.HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")