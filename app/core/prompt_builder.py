def build_prompt(func_data):
    context = f"Class: {func_data['class_context']}" if func_data['class_context'] else "Global Scope"
    
    args_section = "\n".join([f"- {name} ({typ})" for name, typ in func_data['args'].items()]) or "None"

    return f"""
CONTEXT: {context}
FUNCTION NAME: {func_data['name']}
ARGUMENTS:
{args_section}
EXPECTED RETURN: {func_data['returns']}

CODE TO ANALYZE:
{func_data['full_code']}
"""
