from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.agents.orchestrator import orchestrator_node
from src.agents.research import research_node
from src.agents.logistics import logistics_node
from src.agents.budget import budget_node
from src.agents.review import review_node
from src.agents.synthesizer import synthesizer_node

def review_router(state: AgentState) -> str:
    """Decides whether to finalize the trip or go back for revisions."""
    
    qa = state.get("qa_result")
    rev_count = state.get("revision_count", 0)
    
    # Max 3 revisions to prevent infinite loops
    if not qa or qa.get("is_passed") or rev_count >= 3:
        return "synthesizer"
    
    # If we failed, decide where to go back based on feedback
    feedback = " ".join(qa.get("feedback", [])).lower()
    revisions = " ".join(qa.get("suggested_revisions", [])).lower()
    
    if "budget" in feedback or "expensive" in feedback or "cost" in revisions:
        return "budget"
    if "day" in feedback or "itinerary" in feedback or "sequence" in revisions:
        return "logistics"
    
    return "research"

# Initialize the graph
workflow = StateGraph(AgentState)

# Add all 6 REAL nodes
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("research", research_node)
workflow.add_node("logistics", logistics_node)
workflow.add_node("budget", budget_node)
workflow.add_node("review", review_node)
workflow.add_node("synthesizer", synthesizer_node)

# Set the flow
workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", "research")
workflow.add_edge("research", "logistics")
workflow.add_edge("logistics", "budget")
workflow.add_edge("budget", "review")

# The crucial Conditional Edge
workflow.add_conditional_edges(
    "review",
    review_router,
    {
        "synthesizer": "synthesizer",
        "budget": "budget",
        "logistics": "logistics",
        "research": "research"
    }
)

workflow.add_edge("synthesizer", END)

# Compile the graph
graph = workflow.compile()
