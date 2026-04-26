import os
import asyncio
from src.graph.state import AgentState
from src.tools.search import run_search
from src.tools.llm import safe_llm_call

async def research_node(state: AgentState) -> dict:
    """Uses web search to find relevant information based on user constraints."""

    constraints = state.get("constraints")
    if not constraints:
        return {"research_notes": ["No constraints available"], "status": "planning"}

    queries = []
    cities = constraints.get("cities", [])
    prefs = constraints.get("preferences", [])
    country = constraints.get("destination_country", "")

    for city in cities:
        queries.append(f"best things to do in {city} {country} travel guide")
        # Add a preference-specific query if preferences exist
        if prefs:
            queries.append(f"best {prefs[0]} and {prefs[-1]} in {city}")

    all_raw_results = []
    async def perform_search(q):
        print(f"  [RESEARCH] Starting Parallel Search: {q}")
        try:
            results = await asyncio.to_thread(run_search, q, 3)
            if results:
                print(f"  [RESEARCH] Finished Search for: {q} ({len(results)} results)")
                return results
        except Exception as e:
            print(f"  [RESEARCH-WARNING] Search failed for '{q}': {e}")
        return []

    # Run all queries in parallel
    search_tasks = [perform_search(q) for q in queries]
    results_list = await asyncio.gather(*search_tasks)
    
    for results in results_list:
        all_raw_results.extend(results)

    if not all_raw_results:
        print("  [RESEARCH-WARNING] All searches failed, using fallback context")
        all_raw_results = [f"Popular tourist destination: {country}. Cities: {', '.join(cities)}. Known for {', '.join(prefs)}."]

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "research.txt")
    with open(prompt_path, "r") as f:
        system_prompt_template = f.read()

    system_prompt = system_prompt_template.format(constraints=constraints, search_data="")
    human_message = f"Here is the raw search data I found:\n\n{all_raw_results}\n\nPlease summarize this into curated notes."

    print("  [RESEARCH] Summarizing with LLM...")
    try:
        content = await safe_llm_call([
            ("system", system_prompt),
            ("human", human_message)
        ], caller="RESEARCH")

        notes = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                notes.append(line.lstrip("-* ").strip())
        if not notes:
            notes = [content[:500]]

        return {"research_notes": notes, "status": "planning"}
    except Exception as e:
        print(f"  [RESEARCH-ERROR] {e}")
        return {"research_notes": [f"{country} is a popular destination with cities like {', '.join(cities)}."], "status": "planning"}
