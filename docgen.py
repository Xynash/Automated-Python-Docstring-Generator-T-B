import requests
import sys
import os

API_URL = "http://127.0.0.1:8000/generate"

def main():
    if len(sys.argv) < 2:
        print("Usage: docgen <file.py>")
        return

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print("File not found.")
        return

    with open(file_path, "r") as f:
        code = f.read()

    response = requests.post(API_URL, json={"code": code})

    if response.status_code == 200:
        print(response.json()["documented_code"])
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    main()