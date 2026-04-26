import asyncio
from src.tools.llm import safe_llm_call
from src.config import settings

async def test():
    print(f"GOOGLE_KEY starts with: {settings.GOOGLE_API_KEY[:5]}")
    print(f"GROQ_KEY starts with: {settings.GROQ_API_KEY[:5]}")
    try:
        res = await safe_llm_call([("human", "Say hello")])
        print("SUCCESS:", res)
    except Exception as e:
        print("FAILED:", e)

if __name__ == "__main__":
    asyncio.run(test())
