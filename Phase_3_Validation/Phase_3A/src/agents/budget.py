import os
import json
from src.graph.state import AgentState
from src.config import settings
from src.tools.llm import get_llm

def budget_node(state: AgentState) -> dict:
    """Analyzes itinerary costs and validates against user budget."""
    
    constraints = state["constraints"]
    daily_plans = state["daily_plans"]
    accommodation = state["accommodation"]
    intercity_transport = state["intercity_transport"]

    if not constraints or not daily_plans:
        return {"error": "Missing data for budget analysis"}

    # 1. Load the prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "budget.txt")
    with open(prompt_path, "r") as f:
        system_prompt_template = f.read()

    system_prompt = system_prompt_template.format(
        constraints=json.dumps(constraints, indent=2),
        daily_plans=json.dumps(daily_plans, indent=2),
        accommodation=json.dumps(accommodation, indent=2),
        intercity_transport=json.dumps(intercity_transport, indent=2)
    )

    # 2. Initialize LLM
    llm = get_llm()

    # 3. Call LLM
    response = llm.invoke([
        ("system", system_prompt),
        ("human", "Calculate the budget breakdown and status for this itinerary.")
    ])

    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        budget_report = json.loads(content)

        return {
            "budget_report": budget_report,
            "status": "reviewing"
        }
    except Exception as e:
        print(f"Error parsing budget JSON: {e}")
        return {
            "status": "failed",
            "error": f"Budget analysis failed: {str(e)}"
        }
