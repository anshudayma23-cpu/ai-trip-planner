import os
from src.graph.state import AgentState
from src.tools.search import run_search
from src.config import settings
from src.tools.llm import get_llm

def research_node(state: AgentState) -> dict:
    """Uses web search to find relevant information based on user constraints."""
    
    constraints = state["constraints"]
    if not constraints:
        return {"error": "No constraints found in state"}

    # 1. Generate Search Queries
    queries = []
    # Mix cities with preferences and avoidances
    for city in constraints["cities"]:
        # Preference search
        for pref in constraints["preferences"]:
            queries.append(f"best {pref} in {city} {constraints['destination_country']}")
        # Avoidance search (how to avoid things they hate)
        for avoid in constraints["avoidances"]:
            queries.append(f"how to avoid {avoid} in {city} travel tips")
        # General logistics
        queries.append(f"top attractions in {city} {constraints['destination_country']} for {constraints['duration_days']} day trip")

    # 2. Run Searches (Limiting to top 4 unique queries for speed/rate limits)
    unique_queries = list(set(queries))[:4]
    all_raw_results = []
    
    print(f"--- Research Agent: Running {len(unique_queries)} search queries ---")
    for q in unique_queries:
        print(f"Searching: {q}")
        results = run_search(q, max_results=3)
        all_raw_results.extend(results)

    # 3. Summarize with LLM
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "research.txt")
    with open(prompt_path, "r") as f:
        system_prompt_template = f.read()

    system_prompt = system_prompt_template.format(
        constraints=constraints,
        search_data="" # data is passed in human message
    )

    llm = get_llm()

    human_message = f"Here is the raw search data I found:\n\n{all_raw_results}\n\nPlease summarize this into curated notes based on my original constraints."

    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])
    
    # DEBUG
    # print(f"DEBUG LLM Response: {response.content}")
    
    # Parse the list into a clean list of strings (supports -, *, or 1. formats)
    notes = []
    for line in response.content.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Check for bullets or numbered lists
        if line.startswith("- ") or line.startswith("* ") or (line[0].isdigit() and ". " in line):
            # Strip the bullet/number
            clean_note = line.lstrip("-*0123456789. ").strip()
            if clean_note:
                notes.append(clean_note)

    return {
        "research_notes": notes,
        "status": "planning"
    }
