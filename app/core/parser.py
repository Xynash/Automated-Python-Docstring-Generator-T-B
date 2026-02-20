import ast

def extract_functions(code: str):
    tree = ast.parse(code)
    functions = []

    for node in ast.walk(tree):
        # Detect Top-level functions
        if isinstance(node, ast.FunctionDef):
            # Check if it's inside a class
            parent_class = None
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef):
                    if node in parent.body:
                        parent_class = parent.name
            
            functions.append({
                "name": node.name,
                "class_name": parent_class,
                "args": [arg.arg for arg in node.args.args],
                "docstring": ast.get_docstring(node),
                "node": node # Keep reference for unparsing
            })

    return functions