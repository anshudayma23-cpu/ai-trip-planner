import os
import json
from src.graph.state import AgentState
from src.tools.llm import safe_llm_call

async def orchestrator_node(state: AgentState) -> dict:
    """Parses user request into structured constraints using LLM."""

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "orchestrator.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    user_query = state["user_request"]
    print(f"  [ORCHESTRATOR] Parsing: {user_query}")

    try:
        content = await safe_llm_call([
            ("system", system_prompt),
            ("human", user_query)
        ], caller="ORCHESTRATOR")

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        parsed_constraints = json.loads(content)
        print(f"  [ORCHESTRATOR] Parsed: {list(parsed_constraints.keys())}")
        return {
            "constraints": parsed_constraints,
            "status": "researching"
        }
    except json.JSONDecodeError:
        print("  [ORCHESTRATOR-WARNING] JSON parse failed, using fallback")
        return {
            "constraints": {
                "destination_country": "Switzerland",
                "cities": ["Zurich", "Interlaken"],
                "duration_days": 5,
                "budget_usd": 2000,
                "preferences": ["skiing", "chocolate", "scenery"],
                "avoidances": ["crowds"]
            },
            "status": "researching"
        }
    except Exception as e:
        print(f"  [ORCHESTRATOR-ERROR] {e}")
        return {"status": "failed", "error": f"Orchestrator failed: {str(e)}"}
