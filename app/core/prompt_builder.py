# app/core/prompt_builder.py

STYLE_INSTRUCTIONS = {
    "Google": "Use Google Style docstrings.",
    "NumPy": "Use NumPy/SciPy Style docstrings with Parameters and Returns sections separated by dashes.",
    "Sphinx": "Use Sphinx/reStructuredText style with :param:, :type:, :returns:, :rtype: tags.",
    "JSDoc": "Use JSDoc format with @param, @returns, @description tags.",
    "Javadoc": "Use Javadoc format with @param, @return, @throws tags.",
    "Doxygen": "Use Doxygen format with \\param, \\return, \\brief tags (for C++).",
}

LANGUAGE_CONTEXT = {
    "python": "This is a Python function.",
    "javascript": "This is a JavaScript function.",
    "java": "This is a Java method.",
    "cpp": "This is a C++ function.",
}

def build_prompt(func_data, style="Google", language="python"):
    """
    Builds a context-aware prompt for the AI engine.
    Supports multiple languages and docstring styles.
    """
    context = f"Class: {func_data['class_context']}" if func_data.get('class_context') else "Global Scope"

    args_section = "\n".join(
        [f"- {name} ({typ})" for name, typ in func_data.get('args', {}).items()]
    ) or "None"

    style_instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["Google"])
    lang_context = LANGUAGE_CONTEXT.get(language, "This is a code function.")

    return f"""You are an expert software documentation assistant.
{lang_context}
{style_instruction}

CONTEXT: {context}
FUNCTION NAME: {func_data['name']}
ARGUMENTS:
{args_section}
EXPECTED RETURN: {func_data.get('returns', 'Any')}

CODE TO ANALYZE:
{func_data['full_code']}

Write ONLY the docstring content, no code, no explanation. Do not include triple quotes."""