import os
import json
from src.graph.state import AgentState
from src.tools.llm import safe_llm_call

async def review_node(state: AgentState) -> dict:
    """Audits the itinerary for quality, logic, and constraint compliance."""

    constraints = state.get("constraints", {})
    daily_plans = state.get("daily_plans", [])
    budget_report = state.get("budget_report", {})

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "review.txt")
    with open(prompt_path, "r") as f:
        system_prompt_template = f.read()

    system_prompt = system_prompt_template.format(
        constraints=json.dumps(constraints, indent=2),
        daily_plans=json.dumps(daily_plans, indent=2),
        budget_report=json.dumps(budget_report, indent=2)
    )

    print("  [REVIEW] Auditing itinerary...")
    try:
        content = await safe_llm_call([
            ("system", system_prompt),
            ("human", "Audit this itinerary.")
        ], caller="REVIEW")

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        qa_result = json.loads(content)
        is_passed = qa_result.get("is_passed", True)
        new_revision_count = state.get("revision_count", 0)
        if not is_passed:
            new_revision_count += 1

        print(f"  [REVIEW] Complete: {'PASSED' if is_passed else f'NEEDS REVISION ({new_revision_count}/3)'}")
        return {
            "qa_result": qa_result,
            "status": "finalizing" if is_passed else "revising",
            "revision_count": new_revision_count
        }
    except Exception as e:
        print(f"  [REVIEW-WARNING] Parse failed, auto-passing: {e}")
        return {
            "qa_result": {"is_passed": True, "feedback": ["Auto-passed due to parse error"]},
            "status": "finalizing",
            "revision_count": state.get("revision_count", 0)
        }
