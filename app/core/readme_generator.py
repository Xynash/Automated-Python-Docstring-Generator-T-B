from app.core.ai_docstring_engine import client, MODEL

def generate_readme(code: str, filename: str) -> str:
    """
    Generates a professional README.md from any code file.
    """
    if not client:
        raise Exception("AI Client is not initialized.")

    prompt = f"""You are an expert technical writer.
Analyze the following code and generate a professional README.md file.

FILENAME: {filename}
CODE:
{code}

Generate a complete README.md with EXACTLY these sections:

# Project Title (infer from filename or code)

## Description
What this code does in 2-3 sentences.

## Requirements
List any dependencies or requirements needed to run this code.

## Installation
Step by step installation instructions.

## Usage
How to use this code with examples.

## Functions
List all functions/methods with:
- Function name
- What it does
- Parameters
- Return value

## Example
A complete working example showing how to use this code.

RULES:
- Use proper markdown formatting
- Be specific based on the ACTUAL code
- Keep it professional and clear
- Do not add any text outside the README content
"""

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical writer who writes clear, professional README files."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Groq API Error: {str(e)}")