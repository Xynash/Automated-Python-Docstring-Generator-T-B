from app.utils.validators import validate_python_file


def read_python_file(file_path: str) -> str:
    """
    STEP 1–3:
    1. Validate the uploaded Python file
    2. Read file contents
    3. Return code as string
    """

    # Step 2: Validate file (format, existence, size)
    validate_python_file(file_path)

    # Step 3: Read file contents
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
