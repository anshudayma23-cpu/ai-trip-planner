import os
from src.config import settings
from src.graph.state import AgentState, TravelConstraints
from src.graph.workflow import graph

def test_phase_1a():
    print("--- Running Phase 1A Tests ---")
    # Test 2: Config loads
    if settings and settings.GOOGLE_API_KEY:
        print("[PASS] Test 2: Config loads with valid .env")
    else:
        print("[FAIL] Test 2: Config failed to load")

def test_phase_1b():
    print("\n--- Running Phase 1B Tests ---")
    # Test 1 & 2: State instantiation
    try:
        constraints: TravelConstraints = {
            "destination_country": "Japan",
            "cities": ["Tokyo"],
            "duration_days": 5,
            "budget_usd": 1000,
            "preferences": [],
            "avoidances": []
        }
        state: AgentState = {
            "user_request": "test",
            "constraints": constraints,
            "research_notes": [],
            "accommodation": [],
            "daily_plans": [],
            "intercity_transport": [],
            "budget_report": None,
            "qa_result": None,
            "revision_count": 0,
            "status": "init",
            "error": None
        }
        print("[PASS] Test 1 & 2: AgentState & TravelConstraints valid")
    except Exception as e:
        print(f"[FAIL] Test 1 & 2 failed: {e}")

    # Test 3, 4, 5: Graph execution
    try:
        result = graph.invoke({"user_request": "test", "revision_count": 0, "status": "init", "research_notes": []})
        print("[PASS] Test 3, 4, 5: Graph compiles and runs end-to-end")
    except Exception as e:
        print(f"[FAIL] Test 3, 4, 5 failed: {e}")

def test_phase_1c():
    print("\n--- Running Phase 1C Tests (Real LLM) ---")
    test_queries = [
        ("Single City", "3 days in Paris, $1500, love art"),
        ("No Budget", "5 days in Italy, Rome and Florence, love history"),
        ("No Avoidances", "4 days Tokyo, $2000, love anime and food"),
        ("Multiple Avoidances", "5 days Japan, $3000, love food, hate crowds, long walks, and spicy food")
    ]
    
    for name, query in test_queries:
        print(f"Running Test: {name}...")
        try:
            result = graph.invoke({"user_request": query, "revision_count": 0, "status": "parsing", "research_notes": []})
            constraints = result.get("constraints")
            if constraints:
                print(f"[PASS] {name} Passed: {constraints['cities']} | Budget: {constraints['budget_usd']}")
            else:
                print(f"[FAIL] {name} Failed: No constraints returned")
        except Exception as e:
            print(f"[FAIL] {name} Failed with error: {e}")

if __name__ == "__main__":
    test_phase_1a()
    test_phase_1b()
    test_phase_1c()
