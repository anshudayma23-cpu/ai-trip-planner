import json
from src.graph.workflow import graph

def run_test(query: str):
    print(f"\n{'='*50}")
    print(f"TESTING FULL PIPELINE: {query}")
    print(f"{'='*50}\n")
    
    initial_state = {
        "user_request": query,
        "revision_count": 0,
        "status": "parsing",
        "research_notes": []
    }
    
    # Execute the COMPLETE wired pipeline with feedback loop
    result = graph.invoke(initial_state)
    
    # Print Final Itinerary
    print("\n--- FINAL POLISHED ITINERARY ---")
    if result.get("final_itinerary"):
        print(result["final_itinerary"])
        print(f"\nRevisions performed: {result.get('revision_count')}")
        print("\nPipeline Status: SUCCESS")
    else:
        print("Error: No final itinerary generated.")
        if result.get("error"):
            print(f"Details: {result['error']}")

if __name__ == "__main__":
    # Test with canonical query
    run_test("Plan a 5-day trip to Japan. Tokyo and Kyoto. $3000 budget. Love food, hate crowds.")
