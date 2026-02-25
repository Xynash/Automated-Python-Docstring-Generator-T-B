def build_prompt(func_data, style="google"):
    """
    Constructs a prompt that forces the AI to use a specific format.
    """
    context = f"Class: {func_data.get('class_context')}" if func_data.get('class_context') else "Global Scope"
    
    # Logic to explain the style to the AI
    style_guide = ""
    if style.lower() == "numpy":
        style_guide = "Use NumPy format: 'Parameters' and 'Returns' sections with '---' underlines."
    elif style.lower() == "sphinx":
        style_guide = "Use Sphinx format: ':param name:' and ':return:' fields."
    else:
        style_guide = "Use Google format: 'Args:' and 'Returns:' sections."

    return f"""
Generate a Python docstring for the function below.
FORMAT: {style.upper()}
GUIDELINE: {style_guide}

METADATA:
- Name: {func_data.get('name')}
- Context: {context}
- Args: {func_data.get('args')}
- Returns: {func_data.get('returns')}

CODE:
{func_data.get('full_code')}

Return ONLY the docstring.
"""