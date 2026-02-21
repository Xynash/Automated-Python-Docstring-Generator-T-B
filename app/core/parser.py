import ast

def extract_functions(code: str):
    """
    Parses Python code and extracts metadata for all functions and class methods.
    Returns a list of dictionaries containing function nodes and names.
    """
    tree = ast.parse(code)
    functions = []
    processed_nodes = set()

    for node in ast.walk(tree):
        # Handle Functions inside Classes (Methods)
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    functions.append({
                        "name": item.name,
                        "class_name": node.name,
                        "args": [arg.arg for arg in item.args.args],
                        "docstring": ast.get_docstring(item),
                        "node": item
                    })
                    processed_nodes.add(item)
        
        # Handle Top-level functions (Global Scope)
        elif isinstance(node, ast.FunctionDef):
            # Check if we already processed this as a class method
            if node not in processed_nodes:
                functions.append({
                    "name": node.name,
                    "class_name": None,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node),
                    "node": node
                })
                processed_nodes.add(node)

    return functions