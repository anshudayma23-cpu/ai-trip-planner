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
    
    # Execute the full wired pipeline (Orchestrator -> Research -> Logistics -> Budget -> Review)
    result = graph.invoke(initial_state)
    
    # Print QA Results Summary
    print("\n--- QUALITY REVIEW REPORT ---")
    qa = result.get("qa_result")
    if qa:
        status_str = "PASS" if qa['is_passed'] else "FAIL"
        print(f"Status: {status_str}")
        print(f"Score: {qa['score']}/10")
        print("\nFeedback:")
        for f in qa['feedback']:
            print(f"- {f}")
        
        if not qa['is_passed']:
            print("\nSuggested Revisions:")
            for r in qa['suggested_revisions']:
                print(f"- {r}")
        
        print("\nTest Passed: Quality review completed!")
    else:
        print("Error: No QA result generated.")
        if result.get("error"):
            print(f"Details: {result['error']}")

if __name__ == "__main__":
    # Test with a standard query
    run_test("Plan a 5-day trip to Japan. Tokyo and Kyoto. $3000 budget. Love food, hate crowds.")
