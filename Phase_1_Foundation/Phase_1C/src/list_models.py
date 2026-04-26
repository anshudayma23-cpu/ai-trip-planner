import os
import google.generativeai as genai
from src.config import settings

def list_models():
    if not settings or not settings.GOOGLE_API_KEY:
        print("No API key found in settings")
        return
    
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
