# Utility functions
def calculate_hash(text):
    import hashlib
    return hashlib.md5(text.encode()).hexdigest()

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_functions(code):
    import ast
    tree = ast.parse(code)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'lineno': node.lineno,
                'args': [arg.arg for arg in node.args.args]
            })
    return functions

def merge_dicts(*dicts):
    result = {}
    for d in dicts:
        result.update(d)
    return result

class FileProcessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.content = None
    
    def load(self):
        self.content = read_file(self.filepath)
        return self
    
    def process(self):
        if self.content is None:
            raise ValueError("File not loaded")
        return extract_functions(self.content)
    
    def save(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.content)