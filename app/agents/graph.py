from langgraph.graph import StateGraph
from app.agents.state import RecruitingState
from app.agents.nodes import search_node, dedup_node, score_node, pipeline_node, outreach_node, evaluate_node


def create_recruiting_graph():
    """
    Create the recruiting loop agent graph
    """
    workflow = StateGraph(RecruitingState)
    
    # Add nodes to the graph
    workflow.add_node("search", search_node)
    workflow.add_node("dedup", dedup_node)
    workflow.add_node("score", score_node)
    workflow.add_node("pipeline", pipeline_node)
    workflow.add_node("outreach", outreach_node)
    workflow.add_node("evaluate", evaluate_node)
    
    # Define the flow
    workflow.set_entry_point("search")
    workflow.add_edge("search", "dedup")
    workflow.add_edge("dedup", "score")
    workflow.add_edge("score", "pipeline")
    workflow.add_edge("pipeline", "outreach")
    workflow.add_edge("outreach", "evaluate")
    
    # The evaluate node decides whether to finish or loop back
    # For now, we'll have it finish, but in a real implementation
    # it might loop back to search based on conditions
    workflow.add_conditional_edges(
        "evaluate",
        lambda x: "continue" if x.get("continue_loop", False) else "finish",
        {
            "continue": "search",  # Would loop back to search in a real implementation
            "finish": "__end__"
        }
    )
    
    return workflow.compile()