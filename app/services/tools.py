# app/services/tools.py

from typing import Callable, List, Dict, Any
from functools import wraps
from app.core.logger import logger

# ✅ Must be a LIST not a dict
_TOOL_REGISTRY: List[Dict[str, Any]] = []

# -------------------------
# Decorator to auto-register tools
# -------------------------
def tool(name: str, description: str, parameters: Dict[str, Any]):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # ✅ Register tool along with function reference
        _TOOL_REGISTRY.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
            "function_reference": func,  # <-- Important!
        })

        return wrapper
    return decorator

# -------------------------
# Tool implementations (now decorated!)
# -------------------------

@tool(
    name="find_hotels",
    description="Find hotels near a location",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city or area to find hotels near",
            }
        },
        "required": ["location"],
    }
)
async def find_hotels(location: str) -> str:
    logger.info("[Tools] Running 'find_hotels'.")
    return f"Dummy result: Hotels near {location} include Disneyland Hotel, Marriott Anaheim."

@tool(
    name="get_weather",
    description="Get the current weather for a location",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City and country (e.g., Paris, France)",
            }
        },
        "required": ["location"],
    }
)
async def get_weather(location: str) -> str:
    logger.info("[Tools] Running 'get_weather'.")
    return f"Dummy result: It's sunny and 25°C in {location}."

@tool(
    name="search_flights",
    description="Find flights between two cities",
    parameters={
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Departure city or code"},
            "destination": {"type": "string", "description": "Arrival city or code"},
        },
        "required": ["origin", "destination"],
    }
)
async def search_flights(origin: str, destination: str) -> str:
    logger.info("[Tools] Running 'search_flights'.")
    return f"Dummy result: Flights from {origin} to {destination} include Delta DL203 and Air France AF65."

# -------------------------
# API for LLM
# -------------------------
def available_tools() -> List[Dict[str, Any]]:
    """
    Returns all registered tools in OpenAI-compatible JSON format.
    """
    return [tool["function"] for tool in _TOOL_REGISTRY]


# -------------------------
# Dummy runner (for now)
# -------------------------

import json

async def run_tool_locally(tool_call) -> str:
    """
    Executes the tool function locally based on the tool_call information.
    """
    try:
        tool_name = tool_call.function.name
        arguments_str = tool_call.function.arguments

        logger.info(f"[Tools] Received function call: {tool_name} with args {arguments_str}")

        # Parse arguments
        arguments = json.loads(arguments_str)

        # Find corresponding function
        for tool in _TOOL_REGISTRY:
            if tool["function"]["name"] == tool_name:
                func = tool.get("function_reference")
                if func:
                    logger.info(f"[Tools] Executing local tool function: {tool_name}")
                    return await func(**arguments)
        
        logger.warning(f"[Tools] No matching tool found for {tool_name}")
        return "Tool functionality not found."
    
    except Exception as e:
        logger.error(f"[Tools] Error running tool locally: {e}")
        return "An error occurred while running the tool."
