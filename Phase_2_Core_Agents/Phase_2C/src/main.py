import json
from src.agents.logistics import logistics_node

def run_test():
    print("Starting AI Trip Planner Phase 2C Test...")
    print("Testing Logistics Agent (Itinerary Generation)...\n")
    
    # Simulated state from Phase 2B
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
        "research_notes": [
            "Tokyo - Senso-ji: Iconic temple, go before 9AM to avoid crowds.",
            "Tokyo - Tsukiji Outer Market: Best for breakfast sushi and street food snacks.",
            "Kyoto - Yoshida Hill: Peaceful temple experience away from main tourist routes.",
            "Kyoto - Fushimi Inari: Visit at sunrise for solitude among thousands of torii gates.",
            "Transport - Shinkansen: 2.5 hours from Tokyo to Kyoto, very frequent."
        ],
        "accommodation": [],
        "daily_plans": [],
        "intercity_transport": [],
        "revision_count": 0,
        "status": "planning"
    }
    
    result = logistics_node(initial_state)
    
    print("\n--- Generated Itinerary Structure ---")
    if result.get("daily_plans"):
        print(f"Days Planned: {len(result['daily_plans'])}")
        print(f"Accommodation Cities: {[a['city'] for a in result['accommodation']]}")
        
        # Print a sample day
        sample_day = result['daily_plans'][0]
        print(f"\nSample Day {sample_day['day']} in {sample_day['city']}:")
        print(f"  Morning: {sample_day['morning']}")
        print(f"  Afternoon: {sample_day['afternoon']}")
        print(f"  Evening: {sample_day['evening']}")
        
        print("\nTest Passed: Logistics agent generated a structured itinerary!")
    else:
        print("Test Failed: No daily plans generated.")
        if result.get("error"):
            print("Error:", result["error"])

if __name__ == "__main__":
    run_test()
