from src.graph.workflow import graph

def run_test():
    print("Starting AI Trip Planner Skeleton Test...\n")
    
    # Initialize minimal state
    initial_state = {
        "user_request": "Test request",
        "revision_count": 0,
        "status": "initialization",
        "research_notes": []
    }
    
    # Execute the graph
    result = graph.invoke(initial_state)
    
    print("\n--- Final State Summary ---")
    print(f"Status: {result.get('status')}")
    print("Graph execution completed successfully!")

if __name__ == "__main__":
    run_test()
