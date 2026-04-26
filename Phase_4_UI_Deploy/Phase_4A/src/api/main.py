import json
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from src.graph.workflow import graph

app = FastAPI(title="AI Trip Planner API")

class TripRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "AI Trip Planner API is running"}

@app.post("/plan")
async def plan_trip_sync(request: TripRequest):
    """
    Synchronous endpoint for generating a plan.
    """
    initial_state = {
        "user_request": request.query,
        "revision_count": 0,
        "status": "parsing",
        "research_notes": []
    }
    result = graph.invoke(initial_state)
    return result

@app.websocket("/ws/plan")
async def websocket_plan(websocket: WebSocket):
    """
    WebSocket endpoint for live-streaming the agent's progress.
    """
    await websocket.accept()
    try:
        # Receive the query from the user
        data = await websocket.receive_text()
        request_data = json.loads(data)
        query = request_data.get("query")
        
        await websocket.send_json({"type": "info", "message": f"Starting plan for: {query}"})
        
        initial_state = {
            "user_request": query,
            "revision_count": 0,
            "status": "parsing",
            "research_notes": []
        }

        # Use the graph's stream method to get updates after each node
        # Note: In LangGraph, .stream returns the state updates
        for event in graph.stream(initial_state):
            # Extract the current status from the state
            # Each event is a dict mapping node_name -> state_update
            for node_name, state_update in event.items():
                status = state_update.get("status", node_name)
                await websocket.send_json({
                    "type": "status", 
                    "node": node_name,
                    "status": status,
                    "message": f"Agent {node_name} finished. Next: {status}..."
                })
                # Small delay for UI effect
                await asyncio.sleep(0.5)

        # Get the final state to send the itinerary
        final_state = graph.invoke(initial_state)
        await websocket.send_json({
            "type": "final",
            "itinerary": final_state.get("final_itinerary"),
            "revisions": final_state.get("revision_count", 0)
        })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
