import os
from openai import OpenAI
from app.core.prompt_builder import build_prompt

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None


def generate_ai_docstring(func_data, source_code):

    if not client:
        raise Exception("No API key found")

    prompt = build_prompt(func_data, source_code)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": """
You generate professional Python docstrings.

RULES:
- Output ONLY a docstring
- Use Google style
- Infer argument purpose from logic
- Infer correct types
- Never use placeholders
- Never repeat function name
- Summary must describe behavior
- Keep concise but precise

FORMAT:

\"\"\"
Short summary.

Args:
    arg (type): explanation.

Returns:
    type: explanation.
\"\"\"
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    doc = response.choices[0].message.content.strip()

    # safety cleanup
    doc = doc.replace("```python", "").replace("```", "").strip()

    return doc
