import json
from src.graph.workflow import graph

def run_test(query: str, budget: float):
    print(f"\n{'='*50}")
    print(f"TESTING QUERY: {query} (Budget: ${budget})")
    print(f"{'='*50}\n")
    
    # We manually override the budget in the constraints for the test if needed, 
    # but the Orchestrator should pick it up from the query string.
    
    initial_state = {
        "user_request": query,
        "revision_count": 0,
        "status": "parsing",
        "research_notes": []
    }
    
    # Execute the pipeline (Orchestrator -> Research -> Logistics -> Budget)
    result = graph.invoke(initial_state)
    
    # Print Results Summary
    print("\n--- BUDGET REPORT ---")
    report = result.get("budget_report")
    if report:
        print(f"Status: {report['status'].upper()}")
        print(f"Total Estimated: ${report['total_estimated_usd']}")
        print(f"Budget Limit: ${report['budget_limit_usd']}")
        print("\nBreakdown:")
        print(json.dumps(report['breakdown'], indent=2))
        
        if report['status'] == 'red':
            print("\nSavings Suggestions:")
            for s in report['suggestions']:
                print(f"- {s}")
        
        print("\nTest Passed: Budget analysis completed!")
    else:
        print("Error: No budget report generated.")
        if result.get("error"):
            print(f"Details: {result['error']}")

if __name__ == "__main__":
    # Test 1: Realistic Budget
    run_test("Plan a 5-day trip to Japan. Tokyo and Kyoto. $3000 budget.", 3000)
    
    # Test 2: Very Tight Budget (Should trigger Red)
    run_test("Plan a 5-day trip to Japan. Tokyo and Kyoto. $500 budget.", 500)
