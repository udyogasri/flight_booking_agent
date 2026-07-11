import json
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from config import settings

# ============================================================
# Load Flight Data
# ============================================================

try:
    with open("records.json", "r") as f:
        FLIGHTS = json.load(f)
        print(f"✅ Loaded {len(FLIGHTS)} flights from records.json")
except FileNotFoundError:
    print("⚠️ records.json not found, using sample data")
    FLIGHTS = [
        {
            "id": "AI101",
            "airline": "Air India",
            "source": "Bangalore",
            "destination": "Delhi",
            "date": "2026-07-10",
            "departure": "08:30",
            "arrival": "11:20",
            "price": 5200,
            "available_seats": 45,
            "flight_duration": "2h 50m",
            "stops": 0
        },
        {
            "id": "6E401",
            "airline": "IndiGo",
            "source": "Bangalore",
            "destination": "Delhi",
            "date": "2026-07-10",
            "departure": "10:00",
            "arrival": "12:45",
            "price": 4700,
            "available_seats": 32,
            "flight_duration": "2h 45m",
            "stops": 0
        }
    ]

BOOKINGS = {}
MEMORY = MemorySaver()

# ============================================================
# Define Tools
# ============================================================

@tool
def search_flights(
    source: str, 
    destination: str, 
    date: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    airline: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for flights based on source, destination, and optional filters.
    
    Args:
        source: Departure city (e.g., "Bangalore", "Delhi")
        destination: Arrival city (e.g., "Mumbai", "Chennai")
        date: Flight date in YYYY-MM-DD format (optional)
        min_price: Minimum price filter (optional)
        max_price: Maximum price filter (optional)
        airline: Airline name filter (optional)
    
    Returns:
        List of matching flights with details including id, airline, source, 
        destination, date, departure, arrival, price, and availability.
    """
    results = []
    
    for flight in FLIGHTS:
        # Check required fields
        if (flight["source"].lower() != source.lower() or 
            flight["destination"].lower() != destination.lower()):
            continue
            
        # Optional filters
        if date and flight["date"] != date:
            continue
            
        if min_price and flight["price"] < min_price:
            continue
            
        if max_price and flight["price"] > max_price:
            continue
            
        if airline and flight["airline"].lower() != airline.lower():
            continue
            
        # Check if flight has available seats
        if flight.get("available_seats", 0) <= 0:
            continue
            
        results.append(flight)
    
    return results


@tool
def get_flight_details(flight_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific flight by ID.
    
    Args:
        flight_id: The unique identifier of the flight (e.g., "AI101")
    
    Returns:
        Flight details including source, destination, schedule, price, and availability
    """
    for flight in FLIGHTS:
        if flight["id"].lower() == flight_id.lower():
            return flight
    return None


@tool
def book_flight(flight_id: str, passenger_name: str, passenger_email: str) -> Dict[str, Any]:
    """
    Book a flight for a passenger.
    
    Args:
        flight_id: The unique identifier of the flight
        passenger_name: Full name of the passenger
        passenger_email: Email address of the passenger for confirmation
    
    Returns:
        Booking confirmation with booking_id, passenger details, and flight information
    """
    flight = get_flight_details.invoke({"flight_id": flight_id})
    
    if not flight:
        return {"error": "Flight not found"}
    
    # Check availability
    if flight.get("available_seats", 0) <= 0:
        return {"error": "No seats available on this flight"}
    
    # Create booking
    booking_id = str(uuid4())[:8]
    booking = {
        "booking_id": booking_id,
        "passenger": passenger_name,
        "passenger_email": passenger_email,
        "flight": flight,
        "status": "CONFIRMED",
        "booking_time": datetime.now().isoformat()
    }
    
    # Update available seats
    for f in FLIGHTS:
        if f["id"] == flight_id:
            f["available_seats"] = f.get("available_seats", 100) - 1
            break
    
    BOOKINGS[booking_id] = booking
    return booking


@tool
def cancel_booking(booking_id: str) -> Dict[str, Any]:
    """
    Cancel an existing flight booking.
    
    Args:
        booking_id: The unique identifier of the booking to cancel
    
    Returns:
        Updated booking information with status changed to CANCELLED
    """
    booking = BOOKINGS.get(booking_id)
    
    if not booking:
        return {"error": "Booking not found"}
    
    booking["status"] = "CANCELLED"
    booking["cancellation_time"] = datetime.now().isoformat()
    
    # Restore available seat
    flight_id = booking["flight"]["id"]
    for f in FLIGHTS:
        if f["id"] == flight_id:
            f["available_seats"] = f.get("available_seats", 100) + 1
            break
    
    return booking

# ============================================================
# LangGraph State
# ============================================================

class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]

# ============================================================
# LangGraph Components
# ============================================================

class FlightAgent:
    def __init__(self, model_name: str = settings.GROQ_MODEL):
        # Initialize LLM - use Groq directly
        from langchain_groq import ChatGroq
        self.llm = ChatGroq(
            model=model_name, 
            api_key=settings.GROQ_API_KEY,
            temperature=0
        )
        
        # Create tools list
        self.tools = [search_flights, get_flight_details, book_flight, cancel_booking]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build graph
        self.graph = self._build_graph()
        
    def _build_graph(self):
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Define agent node
        def agent_node(state: AgentState):
            messages = state["messages"]
            
            # Add system message if not present
            if not any(isinstance(m, SystemMessage) for m in messages):
                system_prompt = """You are a helpful flight booking assistant. You help users search for flights, 
                get flight details, book flights, and cancel bookings. Always be polite and provide clear information.
                
                When searching for flights, use the search_flights tool. For specific flight details, use get_flight_details.
                For bookings, use book_flight. For cancellations, use cancel_booking.
                
                After finding flights, present them in a clear, organized format. If multiple flights match, 
                highlight the best options based on price, timing, and airline.
                
                Always confirm booking details with the user before finalizing.
                
                Important: When a user asks about flights, ALWAYS use the search_flights tool to get real data.
                Do not make up flight information."""
                
                messages = [SystemMessage(content=system_prompt)] + messages
            
            # Get response from LLM
            response = self.llm_with_tools.invoke(messages)
            
            return {"messages": [response]}
        
        # Define tool node
        def tool_node(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]
            
            # Execute all tool calls
            results = []
            for tool_call in last_message.tool_calls:
                # Find the tool by name
                tool_map = {tool.name: tool for tool in self.tools}
                tool_func = tool_map.get(tool_call["name"])
                
                if tool_func:
                    result = tool_func.invoke(tool_call["args"])
                    results.append(
                        ToolMessage(
                            content=json.dumps(result, default=str),
                            tool_call_id=tool_call["id"]
                        )
                    )
                else:
                    results.append(
                        ToolMessage(
                            content=f"Tool {tool_call['name']} not found",
                            tool_call_id=tool_call["id"]
                        )
                    )
            
            return {"messages": results}
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        def should_continue(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]
            
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return END
        
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        workflow.add_edge("tools", "agent")
        
        # Compile with memory
        return workflow.compile(checkpointer=MEMORY)
    
    def process_message(self, user_message: str, thread_id: str = "default") -> str:
        """Process a user message and return the response"""
        # Prepare input
        config = {"configurable": {"thread_id": thread_id}}
        
        # Add user message
        state = {
            "messages": [HumanMessage(content=user_message)]
        }
        
        # Invoke graph
        result = self.graph.invoke(state, config)
        
        # Extract AI response
        messages = result["messages"]
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and not (hasattr(msg, 'tool_calls') and msg.tool_calls):
                return msg.content
        
        return "I'm sorry, I couldn't process your request."

# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(title="AI Flight Booking Agent")
cors = ["http://localhost:3000"]
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
   CORSMiddleware,
   allow_origins=cors,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# Initialize the agent
agent = FlightAgent()

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    thread_id: str

@app.get("/")
def home():
    return {
        "message": "AI Flight Booking Agent Running",
        "version": "2.0",
        "features": [
            "Natural language flight search",
            "Smart flight recommendations",
            "Seamless booking and cancellation",
            "Conversation memory"
        ]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Process the message
        response = agent.process_message(
            request.message,
            request.thread_id
        )
        
        return ChatResponse(
            response=response,
            thread_id=request.thread_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "flights_available": len(FLIGHTS),
        "total_bookings": len(BOOKINGS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)