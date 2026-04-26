import json
from src.tools.search import run_search
from src.agents.research import research_node
from src.agents.logistics import logistics_node

def test_phase_2a():
    print("--- Running Phase 2A Tests (Search Tool) ---")
    
    # Test 1: Normal Search
    results = run_search("Kyoto temples", max_results=2)
    if len(results) > 0 and isinstance(results[0], str):
        print("[PASS] Test 1: Normal search returns list of strings")
    else:
        print("[FAIL] Test 1: Normal search failed")

    # Test 3: Empty Query
    try:
        empty_res = run_search("", max_results=1)
        # Some APIs return error, some return empty. As long as it doesn't crash the app.
        print("[PASS] Test 3: Empty query handled gracefully")
    except Exception as e:
        print(f"[FAIL] Test 3: Empty query crashed: {e}")

def test_phase_2b():
    print("\n--- Running Phase 2B Tests (Research Agent) ---")
    
    # Test 1 & 2: Multi-city + Avoidances
    state = {
        "constraints": {
            "destination_country": "Japan",
            "cities": ["Tokyo", "Kyoto"],
            "duration_days": 5,
            "budget_usd": 3000,
            "preferences": ["food"],
            "avoidances": ["crowds"]
        },
        "research_notes": []
    }
    
    try:
        result = research_node(state)
        notes = result.get("research_notes", [])
        if len(notes) >= 5:
            print("[PASS] Test 1 & 2: Research Agent extracted multiple notes successfully")
            
            # Check for avoidance logic in notes (heuristically)
            crowd_mention = any("crowd" in n.lower() or "quiet" in n.lower() or "peace" in n.lower() or "early" in n.lower() for n in notes)
            if crowd_mention:
                print("[PASS] Test 2: Avoidance constraint (crowds) addressed in notes")
            else:
                print("[WARN] Test 2: Avoidance constraint not explicitly mentioned in notes (LLM variation)")
        else:
            print("[FAIL] Test 1 & 2: Not enough research notes generated")
    except Exception as e:
        print(f"[FAIL] Test 1 & 2 crashed: {e}")

    # Test 3: Empty constraints/search
    try:
        bad_state = {"constraints": None, "research_notes": []}
        bad_result = research_node(bad_state)
        if "error" in bad_result:
            print("[PASS] Test 3: Missing constraints handled gracefully")
        else:
            print("[FAIL] Test 3: Missing constraints did not return error")
    except Exception as e:
        print(f"[FAIL] Test 3 crashed: {e}")

def test_phase_2c():
    print("\n--- Running Phase 2C Tests (Logistics Agent) ---")
    
    state = {
        "constraints": {
            "destination_country": "Japan",
            "cities": ["Tokyo", "Kyoto"],
            "duration_days": 4,
            "budget_usd": 3000,
            "preferences": ["food"],
            "avoidances": []
        },
        "research_notes": [
            "Tokyo: Tsukiji outer market is great for food.",
            "Kyoto: Fushimi Inari is amazing.",
            "Transport: Take the Shinkansen between Tokyo and Kyoto."
        ],
        "accommodation": [],
        "daily_plans": [],
        "intercity_transport": []
    }
    
    try:
        result = logistics_node(state)
        plans = result.get("daily_plans", [])
        accomm = result.get("accommodation", [])
        transport = result.get("intercity_transport", [])
        
        # Test 1: Duration check
        if len(plans) == 4:
            print("[PASS] Test 1: Exactly 4 daily plans generated")
        else:
            print(f"[FAIL] Test 1: Expected 4 days, got {len(plans)}")
            
        # Test 2: Activity Density
        if all(day.get("morning") and day.get("afternoon") and day.get("evening") for day in plans):
            print("[PASS] Test 2: Morning, afternoon, and evening slots filled for all days")
        else:
            print("[FAIL] Test 2: Some days have missing time slots")
            
        # Test 3: Intercity transport
        if len(transport) > 0:
            print("[PASS] Test 3: Intercity transport (Tokyo <-> Kyoto) planned")
        else:
            print("[WARN] Test 3: No intercity transport explicitly planned (LLM variation)")
            
    except Exception as e:
        print(f"[FAIL] Logistics Agent crashed: {e}")

if __name__ == "__main__":
    test_phase_2a()
    test_phase_2b()
    test_phase_2c()
