# app/core/docstring_gen.py

def generate_docstring(func_data, style="google"):
    """
    Advanced Heuristic-based docstring generator (Fallback Mode).
    Supports Google, NumPy, and Sphinx formatting.
    """
    args = func_data.get("args", {})
    returns = func_data.get("returns", "Any")
    name = func_data.get("name", "function")
    
    indent = " " * 4
    lines = []

    # 1. Summary
    lines.append(f"Executes the logic for the {name} function.")

    # 2. Argument Section (Style-Aware)
    if args:
        lines.append("")
        if style.lower() == "numpy":
            lines.append("Parameters")
            lines.append("----------")
            for arg_name, arg_type in args.items():
                lines.append(f"{arg_name} : {arg_type}")
                lines.append(f"{indent}Description for {arg_name}.")
        elif style.lower() == "sphinx":
            for arg_name, arg_type in args.items():
                lines.append(f":param {arg_name}: Description for {arg_name}.")
                lines.append(f":type {arg_name}: {arg_type}")
        else: # Default: Google
            lines.append("Args:")
            for arg_name, arg_type in args.items():
                lines.append(f"{indent}{arg_name} ({arg_type}): Description for {arg_name}.")

    # 3. Return Section (Style-Aware)
    lines.append("")
    if style.lower() == "numpy":
        lines.append("Returns")
        lines.append("-------")
        lines.append(f"{returns}")
        lines.append(f"{indent}Description of the return value.")
    elif style.lower() == "sphinx":
        lines.append(f":return: Description of the return value.")
        lines.append(f":rtype: {returns}")
    else: # Default: Google
        lines.append("Returns:")
        lines.append(f"{indent}{returns}: Description of the return value.")

    return "\n".join(lines)


def generate_fallback_review(code_metadata):
    """
    Basic static analysis fallback for the 'Code Review' task.
    Used if the AI Reviewer fails.
    """
    return {
        "bugs": [
            {"line": "N/A", "issue": "AI Reviewer currently unavailable.", "fix": "Check syntax manually."}
        ],
        "security": ["Manual audit recommended."],
        "summary": "The system is currently running in Fallback Mode. Automated AI deep-scan is offline."
    }