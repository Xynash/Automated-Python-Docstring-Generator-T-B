import ast


class DocstringInserter(ast.NodeTransformer):
    def __init__(self, target_func_name, docstring):
        self.target_func_name = target_func_name
        self.docstring = docstring

    def visit_FunctionDef(self, node):
        # Only modify target function
        if node.name == self.target_func_name:

            # Skip if docstring already exists
            if ast.get_docstring(node):
                return node

            # Create docstring node (AST handles quoting)
            doc_node = ast.Expr(value=ast.Constant(self.docstring))

            # Insert as first statement
            node.body.insert(0, doc_node)

        return node


def insert_docstring(code: str, func_data: dict, docstring: str) -> str:
    # Try Python AST insertion first
    try:
        tree = ast.parse(code)
        transformer = DocstringInserter(func_data["name"], docstring)
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        return ast.unparse(new_tree)
    except SyntaxError:
        # Non-Python file — insert as comment above function
        return insert_comment_docstring(code, func_data, docstring)

def insert_comment_docstring(code: str, func_data: dict, docstring: str) -> str:
    """
    Inserts docstring as clean // comments inside the function body.
    """
    import re
    func_name = func_data.get("name")
    lines = code.split("\n")
    result = []
    inserted = set()

    # Clean raw docstring
    clean = docstring.strip()
    clean = re.sub(r'^/\*\*\s*', '', clean)
    clean = re.sub(r'\s*\*/$', '', clean)
    clean = clean.strip()

    # Parse docstring into parts
    summary = ""
    params = []
    returns = ""
    raises = ""

    for line in clean.split("\n"):
        line = line.strip().lstrip("* ").strip()
        if not line:
            continue
        if line.startswith("@param"):
            params.append(line.replace("@param", "").strip())
        elif line.startswith("@return"):
            returns = line.replace("@return", "").strip()
        elif line.startswith("@throws") or line.startswith("@raises"):
            raises = line.replace("@throws", "").replace("@raises", "").strip()
        elif not summary:
            summary = line

    def build_comment(func_args, func_data):
        block = []

        # Summary
        if summary:
            block.append(f"        // Method: {summary}")

        # Parameters
        if func_args:
            block.append(f"        //")
            block.append(f"        // Parameters:")
            for arg in func_args:
                block.append(f"        //   {arg} - Description of {arg}")

        # Returns
        ret = returns or func_data.get("returns", "")
        if ret and ret != "void":
            block.append(f"        //")
            block.append(f"        // Returns:")
            block.append(f"        //   {ret}")

        # Raises
        if raises:
            block.append(f"        //")
            block.append(f"        // Raises:")
            block.append(f"        //   {raises}")

        block.append(f"        //")
        return block

    for line in lines:
        result.append(line)
        # Insert right after opening { of the function
        if func_name in line and "(" in line and "{" in line and func_name not in inserted:
            args = func_data.get("args", [])
            comment_block = build_comment(args, func_data)
            result.extend(comment_block)
            inserted.add(func_name)

    return "\n".join(result)