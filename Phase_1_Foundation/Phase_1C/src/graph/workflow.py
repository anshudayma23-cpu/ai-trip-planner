from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.agents.orchestrator import orchestrator_node

def placeholder_node(state: AgentState) -> dict:
    """A pass-through node for testing the graph structure."""
    current_status = state.get("status", "unknown")
    print(f"--- Reached Node with status: {current_status} ---")
    return {"status": current_status}

# Initialize the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_node) # REAL AGENT
workflow.add_node("research", placeholder_node)
workflow.add_node("logistics", placeholder_node)
workflow.add_node("budget", placeholder_node)
workflow.add_node("review", placeholder_node)
workflow.add_node("synthesizer", placeholder_node)

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
