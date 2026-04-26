import os
import json
from src.graph.state import AgentState
from src.config import settings
from src.tools.llm import get_llm

def logistics_node(state: AgentState) -> dict:
    """Creates a detailed day-by-day itinerary based on research notes."""
    
    constraints = state["constraints"]
    research_notes = state["research_notes"]

    if not constraints or not research_notes:
        return {"error": "Missing constraints or research notes for logistics planning"}

    # 1. Load the prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "logistics.txt")
    with open(prompt_path, "r") as f:
        system_prompt_template = f.read()

    system_prompt = system_prompt_template.format(
        constraints=json.dumps(constraints, indent=2),
        research_notes="\n".join([f"- {n}" for n in research_notes])
    )

    # 2. Initialize LLM
    llm = get_llm()

    # 3. Call LLM for structured itinerary
    human_message = "Please generate the structured day-by-day itinerary JSON based on the provided research and constraints."
    
    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    try:
        content = response.content
        # Extract JSON from markdown if necessary
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        itinerary_data = json.loads(content)

        return {
            "accommodation": itinerary_data.get("accommodation", []),
            "intercity_transport": itinerary_data.get("intercity_transport", []),
            "daily_plans": itinerary_data.get("daily_plans", []),
            "status": "budgeting"
        }
    except Exception as e:
        print(f"Error parsing logistics JSON: {e}")
        return {
            "status": "failed",
            "error": f"Logistics planning failed: {str(e)}"
        }
