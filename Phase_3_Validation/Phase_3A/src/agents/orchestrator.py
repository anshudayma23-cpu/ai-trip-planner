import os
import json
from src.graph.state import AgentState, TravelConstraints
from src.config import settings
from src.tools.llm import get_llm

def orchestrator_node(state: AgentState) -> dict:
    """Parses user request into structured constraints using Gemini."""
    
    # 1. Load the prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "orchestrator.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    # 2. Initialize the LLM
    llm = get_llm()

    # 3. Call the LLM
    user_query = state["user_request"]
    messages = [
        ("system", system_prompt),
        ("human", user_query)
    ]
    
    # We force JSON output by using the model's capabilities or explicit prompt instructions
    response = llm.invoke(messages)
    
    try:
        # Extract JSON from response (handling potential markdown formatting)
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        parsed_constraints = json.loads(content)
        
        # 4. Update the state
        return {
            "constraints": parsed_constraints,
            "status": "researching"
        }
    except Exception as e:
        print(f"Error parsing constraints: {e}")
        return {
            "status": "failed",
            "error": f"Failed to parse travel constraints: {str(e)}"
        }
