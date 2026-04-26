import os
import json
from src.graph.state import AgentState
from src.tools.llm import safe_llm_call

async def synthesizer_node(state: AgentState) -> dict:
    """Combines all agent outputs into a final, polished markdown itinerary."""

    constraints = state.get("constraints", {})
    daily_plans = state.get("daily_plans", [])
    accommodation = state.get("accommodation", [])
    intercity_transport = state.get("intercity_transport", [])
    budget_report = state.get("budget_report", {})

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "synthesizer.txt")
    with open(prompt_path, "r") as f:
        system_prompt_template = f.read()

    system_prompt = system_prompt_template.format(
        constraints=json.dumps(constraints, indent=2),
        daily_plans=json.dumps(daily_plans, indent=2),
        accommodation=json.dumps(accommodation, indent=2),
        intercity_transport=json.dumps(intercity_transport, indent=2),
        budget_report=json.dumps(budget_report, indent=2)
    )

    print("  [SYNTHESIZER] Composing final travel guide...")
    try:
        content = await safe_llm_call([
            ("system", system_prompt),
            ("human", "Generate the final polished travel guide in markdown.")
        ], caller="SYNTHESIZER")

        print("  [SYNTHESIZER] Final itinerary generated!")
        return {
            "status": "completed",
            "final_itinerary": content
        }
    except Exception as e:
        print(f"  [SYNTHESIZER-ERROR] {e}")
        # Emergency fallback
        fallback = f"# Trip to {constraints.get('destination_country', 'Your Destination')}\n\n"
        fallback += "## Itinerary\n\n"
        for plan in daily_plans:
            fallback += f"### Day {plan.get('day', '?')}: {plan.get('city', '')}\n"
            fallback += f"- **Morning:** {plan.get('morning', 'Explore the city')}\n"
            fallback += f"- **Afternoon:** {plan.get('afternoon', 'Visit local attractions')}\n"
            fallback += f"- **Evening:** {plan.get('evening', 'Enjoy local cuisine')}\n\n"
        return {
            "status": "completed",
            "final_itinerary": fallback
        }
