import os
import json
from src.graph.state import AgentState
from src.config import settings
from src.tools.llm import get_llm

def review_node(state: AgentState) -> dict:
    """Audits the itinerary for quality, logic, and constraint compliance."""
    
    constraints = state["constraints"]
    daily_plans = state["daily_plans"]
    budget_report = state["budget_report"]

    if not constraints or not daily_plans:
        return {"error": "Missing data for quality review"}

    # 1. Load the prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "review.txt")
    with open(prompt_path, "r") as f:
        system_prompt_template = f.read()

    system_prompt = system_prompt_template.format(
        constraints=json.dumps(constraints, indent=2),
        daily_plans=json.dumps(daily_plans, indent=2),
        budget_report=json.dumps(budget_report, indent=2)
    )

    # 2. Initialize LLM
    llm = get_llm()

    # 3. Call LLM
    response = llm.invoke([
        ("system", system_prompt),
        ("human", "Audit this itinerary and provide a quality score and feedback.")
    ])

    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        qa_result = json.loads(content)

        # Update status and increment revision_count if failed
        is_passed = qa_result.get("is_passed", False)
        next_status = "finalizing" if is_passed else "revising"
        new_revision_count = state.get("revision_count", 0)
        
        if not is_passed:
            new_revision_count += 1

        return {
            "qa_result": qa_result,
            "status": next_status,
            "revision_count": new_revision_count
        }
    except Exception as e:
        print(f"Error parsing review JSON: {e}")
        return {
            "status": "failed",
            "error": f"Quality review failed: {str(e)}"
        }
