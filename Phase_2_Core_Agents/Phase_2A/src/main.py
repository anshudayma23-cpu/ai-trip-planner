from src.tools.search import run_search

def run_test():
    print("Starting AI Trip Planner Phase 2A Test...")
    print("Testing Search Tool with Fallback Logic...\n")
    
    query = "best historical temples in Kyoto for avoiding crowds"
    print(f"Query: {query}")
    
    results = run_search(query, max_results=3)
    
    print("\n--- Search Results ---")
    if results:
        for i, res in enumerate(results):
            print(f"\nResult {i+1}:")
            print(res[:200] + "...") # Print snippet
        print("\nTest Passed: Search successful!")
    else:
        print("Test Failed: No results returned.")

if __name__ == "__main__":
    run_test()
