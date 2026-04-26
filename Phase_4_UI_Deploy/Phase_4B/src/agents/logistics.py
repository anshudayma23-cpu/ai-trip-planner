import os
import json
from src.graph.state import AgentState
from src.tools.llm import safe_llm_call

async def logistics_node(state: AgentState) -> dict:
    """Creates a detailed day-by-day itinerary based on research notes."""

    constraints = state.get("constraints", {})
    research_notes = state.get("research_notes", [])

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "logistics.txt")
    with open(prompt_path, "r") as f:
        system_prompt_template = f.read()

    system_prompt = system_prompt_template.format(
        constraints=json.dumps(constraints, indent=2),
        research_notes="\n".join([f"- {n}" for n in research_notes])
    )

    print("  [LOGISTICS] Building itinerary...")
    try:
        content = await safe_llm_call([
            ("system", system_prompt),
            ("human", "Generate the itinerary JSON.")
        ], caller="LOGISTICS")

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        itinerary_data = json.loads(content)
        print(f"  [LOGISTICS] Itinerary created: {len(itinerary_data.get('daily_plans', []))} days")
        return {
            "accommodation": itinerary_data.get("accommodation", []),
            "intercity_transport": itinerary_data.get("intercity_transport", []),
            "daily_plans": itinerary_data.get("daily_plans", []),
            "status": "budgeting"
        }
    except Exception as e:
        print(f"  [LOGISTICS-ERROR] {e}")
        return {"status": "failed", "error": str(e)}
