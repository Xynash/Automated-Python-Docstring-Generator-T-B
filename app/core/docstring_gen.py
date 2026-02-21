# app/core/docstring_gen.py

def generate_docstring(func_data):
    """
    Heuristic-based docstring generator (Fallback Mode).
    Used when AI is toggled off or the API fails.
    """
    args = func_data.get("args", {})
    returns = func_data.get("returns", "Any")
    
    # We use func_data.get("name") to avoid errors if key is missing
    name = func_data.get("name", "function")
    
    indent = " " * 4
    lines = []

    # Summary (Simple placeholder)
    lines.append(f"Executes the {name} logic.")

    # Args Section
    if args:
        lines.append("")
        lines.append("Args:")
        for arg_name, arg_type in args.items():
            lines.append(f"{indent}{arg_name} ({arg_type}): Description for {arg_name}.")

    # Returns Section
    lines.append("")
    lines.append("Returns:")
    lines.append(f"{indent}{returns}: Description of the return value.")

    return "\n".join(lines)