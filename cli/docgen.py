import sys
import requests

if len(sys.argv) < 2:
    print("Usage: python docgen.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]

with open(file_path, "r") as f:
    code = f.read()

# Send code to FastAPI backend
response = requests.post(
    "http://127.0.0.1:8000/generate",
    json={"code": code, "style": "google"}
)

if response.status_code == 200:
    documented_code = response.json().get("documented_code", "")
    with open(file_path, "w") as f:
        f.write(documented_code)
    print(f"✅ Docstrings generated in {file_path}")
else:
    print("❌ Failed to generate docstrings:", response.text)