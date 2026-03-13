def build_prompt(func_data, style="google"):
    """
    Constructs a detailed prompt for high quality docstring generation.
    """
    # Safety check - if string is passed instead of dict
    if isinstance(func_data, str):
        return f"Generate a Python docstring for this code:\n{func_data}"

    context = f"Class: {func_data.get('class_context')}" if func_data.get('class_context') else "Global Scope"
    # Detailed style guides
    if style.lower() == "numpy":
        style_guide = """Use NumPy format exactly like this:
Short one line summary.

Parameters
----------
param_name : type
    Description of parameter.

Returns
-------
type
    Description of return value.

Raises
------
ErrorType
    When this error occurs.

Examples
--------
>>> function_call()
result
"""
    elif style.lower() == "sphinx":
        style_guide = """Use Sphinx format exactly like this:
Short one line summary.

:param param_name: Description of parameter.
:type param_name: type
:returns: Description of return value.
:rtype: type
:raises ErrorType: When this error occurs.

Example::

    result = function_call()
"""
    else:
        style_guide = """Use Google format exactly like this:
Short one line summary.

Args:
    param_name (type): Description of parameter.

Returns:
    type: Description of return value.

Raises:
    ErrorType: When this error occurs.

Example:
    >>> function_call()
    result
"""

    return f"""You are an expert Python documentation writer.
Your job is to write a high quality, accurate, and detailed docstring.

STRICT RULES:
1. Read the actual CODE carefully before writing
2. First line must be a clear one-line summary of what the function ACTUALLY does
3. Describe each argument accurately based on how it is ACTUALLY used in the code
4. Describe the return value accurately based on what is ACTUALLY returned
5. Only add Raises section if the function ACTUALLY raises errors
6. Add a realistic Example showing how to call the function
7. Return ONLY the docstring content — no triple quotes, no extra text

STYLE: {style.upper()}
{style_guide}

FUNCTION DETAILS:
- Name: {func_data.get('name')}
- Location: {context}
- Arguments: {func_data.get('args')}
- Returns: {func_data.get('returns')}

ACTUAL CODE TO DOCUMENT:
{func_data.get('full_code')}

Now write the {style.upper()} style docstring for this function:
"""