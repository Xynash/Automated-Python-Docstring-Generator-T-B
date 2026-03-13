import os

def validate_python_file(file_path: str) -> None:

    if not file_path:
        raise ValueError("File path is empty")
    
    if not file_path.endswith(".py"):
        raise ValueError("Only .py files are allowed")

    if not os.path.exists(file_path):
        raise FileNotFoundError("Python file does not exist")

    if os.path.getsize(file_path) == 0:
        raise ValueError("Python file is empty")