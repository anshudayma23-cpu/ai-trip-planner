import json
from src.graph.workflow import graph

def run_test(query: str):
    print(f"\n{'='*50}")
    print(f"TESTING QUERY: {query}")
    print(f"{'='*50}\n")
    
    initial_state = {
        "user_request": query,
        "revision_count": 0,
        "status": "parsing",
        "research_notes": []
    }
    
    # Execute the full wired pipeline
    result = graph.invoke(initial_state)
    
    # Print Results Summary
    print("\n--- TEST COMPLETED ---")
    print(f"Final Status: {result.get('status')}")
    
    if result.get("daily_plans"):
        print(f"Generated a {len(result['daily_plans'])}-day itinerary successfully!")
        # Print just the first day as a sample
        day1 = result['daily_plans'][0]
        print(f"Day 1 Sample: {day1['morning']} | {day1['afternoon']}")
    else:
        print("Error: No itinerary generated.")
        if result.get("error"):
            print(f"Details: {result['error']}")

if __name__ == "__main__":
    # Test cases for Phase 2D
    test_queries = [
        "Plan a 5-day trip to Japan. Tokyo + Kyoto. $3,000 budget. Food and temples. Hate crowds.",
        "3-day Paris trip, $1500, museums and cafes",
        "4-day Thailand trip, Bangkok, $2000, street food and night markets"
    ]
    
    for query in test_queries:
        run_test(query)
