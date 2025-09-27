import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access the key
api_key = os.getenv("GEMINI_API_KEY")

print("API Key:", api_key)