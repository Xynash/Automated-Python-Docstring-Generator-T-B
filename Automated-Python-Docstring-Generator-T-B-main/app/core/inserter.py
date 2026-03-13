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
    tree = ast.parse(code)

    transformer = DocstringInserter(func_data["name"], docstring)
    new_tree = transformer.visit(tree)

    ast.fix_missing_locations(new_tree)

    return ast.unparse(new_tree)
