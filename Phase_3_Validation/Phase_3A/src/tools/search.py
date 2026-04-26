import time
from langchain_community.tools.tavily_search import TavilySearchResults
from src.config import settings

def run_search(query: str, max_results: int = 5) -> list[str]:
    """
    Executes a web search using Tavily.
    Includes fallback logic for secondary API keys if the primary limit is hit.
    """
    
    # List of keys to try
    keys = [settings.TAVILY_API_KEY]
    if settings.TAVILY_API_KEY_SECONDARY:
        keys.append(settings.TAVILY_API_KEY_SECONDARY)
        
    last_exception = None
    
    for i, key in enumerate(keys):
        try:
            print(f"--- Attempting search with Key {i+1} ---")
            search_tool = TavilySearchResults(
                api_key=key,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True
            )
            
            results = search_tool.invoke({"query": query})
            
            # Clean up results to just text content
            if isinstance(results, list):
                return [r["content"] for r in results if "content" in r]
            return []
            
        except Exception as e:
            last_exception = e
            error_msg = str(e).lower()
            
            # Check if it's a rate limit or credit issue
            if "limit" in error_msg or "credit" in error_msg or "403" in error_msg:
                print(f"Key {i+1} failed (Limit/Credit). Checking for fallback...")
                continue # Try the next key
            else:
                print(f"Search failed with unexpected error: {e}")
                break # Don't retry for other errors
                
    # If we get here, all keys failed or an unexpected error occurred
    print(f"All search attempts failed: {last_exception}")
    return []
