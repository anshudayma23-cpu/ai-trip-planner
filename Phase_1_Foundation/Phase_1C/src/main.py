import json
from src.graph.workflow import graph

def run_test():
    print("Starting AI Trip Planner Phase 1C Test...")
    print("Sending request to Gemini for parsing...\n")
    
    # 1. Input natural language request
    user_request = "Plan a 5-day trip to Japan. Tokyo + Kyoto. $3,000 budget. Love food and temples, hate crowds."
    
    initial_state = {
        "user_request": user_request,
        "revision_count": 0,
        "status": "parsing",
        "research_notes": []
    }
    
    # 2. Execute the graph
    # This will run Orchestrator (Real LLM) -> Research (Placeholder) -> ...
    result = graph.invoke(initial_state)
    
    # 3. Print Results
    print("\n--- Extraction Results ---")
    if result.get("constraints"):
        print(json.dumps(result["constraints"], indent=2))
        print("\nStatus successfully transitioned to:", result.get("status"))
        print("Test Passed: Intent Parsing Successful!")
    else:
        print("Test Failed: Constraints not found in state.")
        if result.get("error"):
            print("Error:", result["error"])

if __name__ == "__main__":
    run_test()
