import os
# from openai import OpenAI  <-- COMMENTED OUT
from dotenv import load_dotenv
from app.core.prompt_builder import build_prompt

# 1. Load environment variables from .env file
load_dotenv()

# 2. Retrieve API Key
API_KEY = os.getenv("OPENAI_API_KEY")

# 3. Client set to None to avoid library requirement
client = None 

def generate_ai_docstring(func_data):
    """
    AI generation is currently disabled.
    """
    raise Exception("AI mode is disabled. Please install 'openai' library to enable.")