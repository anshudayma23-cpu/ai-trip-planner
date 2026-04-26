import os
from groq import Groq
from dotenv import load_dotenv

# Load .env from root
load_dotenv("../../.env")

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("GROQ_API_KEY not found in .env")
    exit(1)

client = Groq(api_key=api_key)
models = client.models.list()

print("--- Available Groq Models ---")
for model in models.data:
    print(f"ID: {model.id}")
