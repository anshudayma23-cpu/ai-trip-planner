import os
import json
from src.graph.state import AgentState
from src.tools.llm import safe_llm_call

async def budget_node(state: AgentState) -> dict:
    """Analyzes itinerary costs and validates against user budget."""

    constraints = state.get("constraints", {})
    daily_plans = state.get("daily_plans", [])
    accommodation = state.get("accommodation", [])
    intercity_transport = state.get("intercity_transport", [])

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "budget.txt")
    with open(prompt_path, "r") as f:
        system_prompt_template = f.read()

    system_prompt = system_prompt_template.format(
        constraints=json.dumps(constraints, indent=2),
        daily_plans=json.dumps(daily_plans, indent=2),
        accommodation=json.dumps(accommodation, indent=2),
        intercity_transport=json.dumps(intercity_transport, indent=2)
    )

    print("  [BUDGET] Calculating costs...")
    try:
        content = await safe_llm_call([
            ("system", system_prompt),
            ("human", "Calculate budget.")
        ], caller="BUDGET")

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        print("  [BUDGET] Analysis complete")
        return {"budget_report": json.loads(content), "status": "reviewing"}
    except Exception as e:
        print(f"  [BUDGET-ERROR] {e}")
        return {"status": "failed", "error": str(e)}
