import re

def detect_language(code: str) -> str:
    """
    Auto detects programming language from code patterns.
    """
    if re.search(r'public\s+(class|static|void|int|String)|System\.out\.print', code):
        return "java"
    if re.search(r'#include\s*<\w+>|std::|cout\s*<<|cin\s*>>', code):
        return "cpp"
    if re.search(r'#include\s*<stdio\.h>|printf\s*\(|scanf\s*\(', code):
        return "c"
    if re.search(r'const\s+\w+\s*=|let\s+\w+\s*=|function\s+\w+\s*\(|=>\s*{|console\.log', code):
        return "javascript"
    return "python"


def get_style_guide(style: str, language: str) -> str:
    """
    Returns correct style guide based on language.
    Python supports Google/NumPy/Sphinx.
    Other languages use their native format.
    """

    # JavaScript always JSDoc
    if language == "javascript":
        return """Use JSDoc format exactly like this:
/**
 * Short one line summary.
 *
 * @param {type} paramName - Description of parameter.
 * @returns {type} Description of return value.
 * @throws {ErrorType} When this error occurs.
 *
 * @example
 * // Example usage
 * functionCall(args);
 */"""

    # Java always Javadoc
    if language == "java":
        return """Use Javadoc format exactly like this:
/**
 * Short one line summary.
 *
 * @param paramName Description of parameter.
 * @return Description of return value.
 * @throws ExceptionType When this error occurs.
 *
 * Example:
 * functionCall(args);
 */"""

    # C and C++ always Doxygen
    if language in ["c", "cpp"]:
        return """Use Doxygen format exactly like this:
/**
 * @brief Short one line summary.
 *
 * @param paramName Description of parameter.
 * @return Description of return value.
 * @throws ErrorType When this error occurs.
 *
 * @example
 * functionCall(args);
 */"""

    # Python supports all 3 styles
    if style.lower() == "numpy":
        return """Use NumPy format exactly like this:
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
        return """Use Sphinx format exactly like this:
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
        return """Use Google format exactly like this:
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


def build_prompt(func_data, style="google", language=None):
    """
    Constructs a detailed prompt for high quality docstring generation.
    Supports Python, JavaScript, Java, C and C++.
    All existing features preserved.
    """
    # Safety check - if string is passed instead of dict
    if isinstance(func_data, str):
        return f"Generate a docstring for this code:\n{func_data}"

    context = f"Class: {func_data.get('class_context')}" if func_data.get('class_context') else "Global Scope"

    # Auto detect language if not provided
    if not language or language == "auto":
        language = detect_language(func_data.get("full_code", ""))

    style_guide = get_style_guide(style, language)

    return f"""You are an expert {language} documentation writer.
Your job is to write a high quality, accurate, and detailed docstring.

LANGUAGE: {language.upper()}

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

Now write the {language.upper()} docstring for this function:
"""