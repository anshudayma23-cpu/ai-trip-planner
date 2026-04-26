from src.agents.research import research_node

def run_test():
    print("Starting AI Trip Planner Phase 2B Test...")
    print("Testing Research Agent (Search + Summarization)...\n")
    
    # Simulated state from Phase 1C
    initial_state = {
        "user_request": "5-day trip to Japan. Tokyo + Kyoto. $3000 budget. Food and temples. Hate crowds.",
        "constraints": {
            "destination_country": "Japan",
            "cities": ["Tokyo", "Kyoto"],
            "duration_days": 5,
            "budget_usd": 3000,
            "preferences": ["food", "temples"],
            "avoidances": ["crowds"]
        },
        "research_notes": [],
        "revision_count": 0,
        "status": "researching"
    }
    
    result = research_node(initial_state)
    
    print("\n--- Curated Research Notes ---")
    if result.get("research_notes"):
        for i, note in enumerate(result["research_notes"]):
            print(f"{i+1}. {note}")
        print("\nTest Passed: Research agent generated curated notes!")
    else:
        print("Test Failed: No notes generated.")
        if result.get("error"):
            print("Error:", result["error"])

if __name__ == "__main__":
    run_test()
