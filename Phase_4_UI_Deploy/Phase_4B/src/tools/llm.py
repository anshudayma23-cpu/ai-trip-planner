from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from src.config import settings


def get_llm(model_name: str = None):
    """
    Returns the primary LLM. If primary is Gemini, returns Gemini.
    """
    if model_name is None:
        model_name = settings.PRIMARY_MODEL

    if "gemini" in model_name.lower():
        print(f"  [LLM] Using Gemini: {model_name}")
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3,
            max_retries=2
        )
    else:
        print(f"  [LLM] Using Groq: {model_name}")
        return ChatGroq(
            model_name=model_name,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0.3,
            max_retries=2
        )


async def safe_llm_call(messages: list, caller: str = "unknown") -> str:
    """
    Tries PRIMARY model first, then FALLBACK model.
    Returns the response content string, or raises if both fail.
    """
    # Try primary (Gemini 1.5 Flash)
    try:
        llm = get_llm(settings.PRIMARY_MODEL)
        print(f"  [{caller}] Calling primary: {settings.PRIMARY_MODEL}")
        response = await llm.ainvoke(messages)
        print(f"  [{caller}] Primary succeeded")
        return response.content
    except Exception as e:
        print(f"  [{caller}] Primary failed: {type(e).__name__}: {str(e)[:100]}")

    # Try fallback (Groq Llama)
    try:
        llm = get_llm(settings.FALLBACK_MODEL)
        print(f"  [{caller}] Calling fallback: {settings.FALLBACK_MODEL}")
        response = await llm.ainvoke(messages)
        print(f"  [{caller}] Fallback succeeded")
        return response.content
    except Exception as e:
        print(f"  [{caller}] Fallback also failed: {type(e).__name__}: {str(e)[:100]}")
        raise RuntimeError(f"Both LLM providers failed for {caller}: {e}")
