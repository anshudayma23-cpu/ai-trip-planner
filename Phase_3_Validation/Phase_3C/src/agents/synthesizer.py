import os
import json
from src.graph.state import AgentState
from src.config import settings
from src.tools.llm import get_llm

def synthesizer_node(state: AgentState) -> dict:
    """Combines all agent outputs into a final, polished markdown itinerary."""
    
    constraints = state["constraints"]
    daily_plans = state["daily_plans"]
    accommodation = state["accommodation"]
    intercity_transport = state["intercity_transport"]
    budget_report = state["budget_report"]

    if not constraints or not daily_plans:
        return {"error": "Missing data for final synthesis"}

    # 1. Load the prompt
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

    # 2. Initialize LLM
    llm = get_llm()

    # 3. Call LLM
    response = llm.invoke([
        ("system", system_prompt),
        ("human", "Generate the final polished travel guide in Markdown.")
    ])

    return {
        "status": "completed",
        "final_itinerary": response.content # We should add this to state or just return it
    }
