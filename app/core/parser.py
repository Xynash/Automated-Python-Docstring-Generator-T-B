import ast
import re


def extract_functions(code: str, language: str = "python"):
    """
    Universal parser for Python, Java, JavaScript, C and C++.
    Routes to the correct parser based on language.
    """
    if language == "python":
        return extract_python_functions(code)
    elif language == "java":
        return extract_java_functions(code)
    elif language == "javascript":
        return extract_javascript_functions(code)
    elif language in ["c", "cpp"]:
        return extract_c_functions(code)
    else:
        return extract_python_functions(code)


def extract_python_functions(code: str):
    """
    Original Python AST parser — unchanged.
    """
    tree = ast.parse(code)
    functions = []
    processed_nodes = set()

    for node in ast.walk(tree):
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

        elif isinstance(node, ast.FunctionDef):
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


def extract_java_functions(code: str):
    """
    Extracts Java methods using regex.
    """
    functions = []

    # Match class name
    class_match = re.search(r'class\s+(\w+)', code)
    class_name = class_match.group(1) if class_match else None

    # Match Java methods
    pattern = re.compile(
        r'(public|private|protected)?\s*(static)?\s*(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{',
        re.MULTILINE
    )

    for match in pattern.finditer(code):
        return_type = match.group(3)
        name = match.group(4)
        args_raw = match.group(5).strip()

        # Skip class declarations
        if name in ["class", "interface", "enum"]:
            continue

        # Parse args
        args = []
        if args_raw:
            for arg in args_raw.split(","):
                parts = arg.strip().split()
                if len(parts) >= 2:
                    args.append(parts[-1])

        functions.append({
            "name": name,
            "class_name": class_name,
            "args": args,
            "docstring": None,
            "node": None,
            "returns": return_type,
            "full_code": match.group(0)
        })

    return functions


def extract_javascript_functions(code: str):
    """
    Extracts JavaScript functions using regex.
    """
    functions = []

    patterns = [
        # Regular functions
        re.compile(r'function\s+(\w+)\s*\(([^)]*)\)', re.MULTILINE),
        # Arrow functions
        re.compile(r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>', re.MULTILINE),
        # Method shorthand
        re.compile(r'(\w+)\s*\(([^)]*)\)\s*\{', re.MULTILINE),
    ]

    seen = set()
    for pattern in patterns:
        for match in pattern.finditer(code):
            name = match.group(1)
            args_raw = match.group(2).strip()

            if name in seen or name in ["if", "for", "while", "switch"]:
                continue
            seen.add(name)

            args = [a.strip() for a in args_raw.split(",") if a.strip()]

            functions.append({
                "name": name,
                "class_name": None,
                "args": args,
                "docstring": None,
                "node": None,
                "returns": "Any",
                "full_code": match.group(0)
            })

    return functions


def extract_c_functions(code: str):
    """
    Extracts C and C++ functions using regex.
    """
    functions = []

    pattern = re.compile(
        r'(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{',
        re.MULTILINE
    )

    seen = set()
    for match in pattern.finditer(code):
        return_type = match.group(1)
        name = match.group(2)
        args_raw = match.group(3).strip()

        if name in seen or return_type in ["if", "for", "while", "switch"]:
            continue
        seen.add(name)

        args = []
        if args_raw and args_raw != "void":
            for arg in args_raw.split(","):
                parts = arg.strip().split()
                if parts:
                    args.append(parts[-1])

        functions.append({
            "name": name,
            "class_name": None,
            "args": args,
            "docstring": None,
            "node": None,
            "returns": return_type,
            "full_code": match.group(0)
        })

    return functions