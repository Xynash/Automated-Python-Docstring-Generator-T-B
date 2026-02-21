import ast

def infer_return_type(node):
    """Extracts actual type hints if they exist, otherwise analyzes returns."""
    if node.returns:
        return ast.unparse(node.returns)
    
    for child in ast.walk(node):
        if isinstance(child, ast.Return) and child.value:
            if isinstance(child.value, ast.Constant):
                return type(child.value.value).__name__
    return "Any"

def get_arg_metadata(node):
    """Extracts arguments and their type hints."""
    args_meta = {}
    for arg in node.args.args:
        if arg.arg == 'self': continue
        annotation = ast.unparse(arg.annotation) if arg.annotation else "Any"
        args_meta[arg.arg] = annotation
    return args_meta

def analyze_function(node: ast.FunctionDef, class_name=None):
    """Prepares clean metadata for the AI Engine."""
    return {
        "name": node.name,
        "class_context": class_name,
        "args": get_arg_metadata(node),
        "returns": infer_return_type(node),
        "docstring": ast.get_docstring(node),
        "full_code": ast.unparse(node) # Crucial for AI to understand logic
    }