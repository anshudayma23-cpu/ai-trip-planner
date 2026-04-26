from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.agents.orchestrator import orchestrator_node
from src.agents.research import research_node
from src.agents.logistics import logistics_node
from src.agents.budget import budget_node
from src.agents.review import review_node

def synthesizer_placeholder(state: AgentState) -> dict:
    """A pass-through node for final synthesis."""
    print("--- [Placeholder] Reached Node: synthesizer ---")
    return {"status": "completed"}

# Initialize the graph
workflow = StateGraph(AgentState)

# Add nodes (REAL agents for first 5 steps)
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("research", research_node)
workflow.add_node("logistics", logistics_node)
workflow.add_node("budget", budget_node)
workflow.add_node("review", review_node)

# Placeholder for final phase
workflow.add_node("synthesizer", synthesizer_placeholder)

# Set the flow
workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", "research")
workflow.add_edge("research", "logistics")
workflow.add_edge("logistics", "budget")
workflow.add_edge("budget", "review")
workflow.add_edge("review", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile the graph
graph = workflow.compile()
