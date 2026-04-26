import json
import asyncio
import os
import traceback
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.graph.workflow import graph
import hashlib

# Simple in-memory cache for identical queries
query_cache = {}

def get_cache_key(query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest()

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(title="AI Trip Planner API")

# Enable CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

class TripRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.post("/plan")
async def plan_trip_sync(request: TripRequest):
    initial_state = {
        "user_request": request.query,
        "revision_count": 0,
        "status": "parsing",
        "research_notes": []
    }
    result = await graph.ainvoke(initial_state)
    return result

@app.websocket("/ws/plan")
async def websocket_plan(websocket: WebSocket):
    await websocket.accept()
    print("--- WebSocket Connection Opened ---")
    
    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)
        query = request_data.get("query")
        print(f"--- Received Query: {query} ---")
        
        cache_key = get_cache_key(query)
        if cache_key in query_cache:
            print(f"--- CACHE HIT FOR: {query} ---")
            await websocket.send_json({"type": "status", "node": "cache", "status": "completed", "message": "Loaded from cache instantly!"})
            await websocket.send_json({
                "type": "final",
                "itinerary": query_cache[cache_key]["final_itinerary"],
                "revisions": query_cache[cache_key]["revision_count"]
            })
            return

        await websocket.send_json({"type": "status", "node": "orchestrator", "status": "initializing", "message": "Initializing Swarm..."})
        
        initial_state = {
            "user_request": query,
            "revision_count": 0,
            "status": "parsing",
            "research_notes": []
        }

        final_state = initial_state

        print("--- Starting Graph Stream ---")
        async for event in graph.astream(initial_state):
            print(f"--- Stream Event: {list(event.keys())} ---")
            for node_name, state_update in event.items():
                final_state.update(state_update)
                status = state_update.get("status", node_name)
                
                await websocket.send_json({
                    "type": "status", 
                    "node": node_name,
                    "status": status,
                    "message": f"Agent {node_name.capitalize()} completed task."
                })

        print("--- Sending Final Result ---")
        
        # Save to cache ONLY if it's a real itinerary
        itinerary = final_state.get("final_itinerary")
        is_real_itinerary = itinerary and "Day 1:" in itinerary
        
        if is_real_itinerary:
            query_cache[cache_key] = {
                "final_itinerary": itinerary,
                "revision_count": final_state.get("revision_count", 0)
            }
            print(f"--- Cached successfully: {query[:30]}... ---")
        else:
            print("--- Skipping cache: Incomplete/Fallback itinerary ---")

        await websocket.send_json({
            "type": "final",
            "itinerary": final_state.get("final_itinerary"),
            "revisions": final_state.get("revision_count", 0)
        })

    except WebSocketDisconnect:
        print("--- WebSocket Disconnected by Client ---")
    except Exception as e:
        print(f"--- CRITICAL ERROR: {str(e)} ---")
        traceback.print_exc()
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
        print("--- Connection Cleaned Up ---")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
