import os
from openai import OpenAI  
from dotenv import load_dotenv
from app.core.prompt_builder import build_prompt

# 1. Load environment variables from .env file
load_dotenv()

# 2. Retrieve API Key
API_KEY = os.getenv("OPENAI_API_KEY")

# 3. Client set to None to avoid library requirement
client = OpenAI(api_key=API_KEY) 

def generate_ai_docstring(func_data, style="Google", language="python"):
    """
    Generates a docstring using OpenAI GPT.
    Now supports style and language parameters.
    """
    prompt = build_prompt(func_data, style=style, language=language)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",        # cheap and fast; change to gpt-4 if needed
        messages=[
            {"role": "system", "content": "You are an expert code documentation assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.3               # low temp = consistent, factual output
    )

    return response.choices[0].message.content.strip()
