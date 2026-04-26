from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from src.config import settings

def get_llm(model_name: str = None):
    """
    Returns the appropriate ChatModel instance based on the model name.
    Supports Google Gemini and Groq (Llama).
    """
    if model_name is None:
        model_name = settings.PRIMARY_MODEL
        
    if "gemini" in model_name.lower():
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0
        )
    elif "llama" in model_name.lower() or "mixtral" in model_name.lower():
        return ChatGroq(
            model_name=model_name,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0
        )
    else:
        # Default to Groq if unknown, as it's our current unblocker
        return ChatGroq(
            model_name=settings.PRIMARY_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0
        )
