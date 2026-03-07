import requests
import argparse
import os

API_URL = "http://127.0.0.1:8000/generate"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to Python file")
    parser.add_argument("--style", default="google",
                        help="Docstring style (google/numpy/sphinx)")
    
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print("File not found.")
        return

    with open(args.file, "r") as f:
        code = f.read()

    response = requests.post(API_URL, json={
        "code": code,
        "style": args.style
    })

    if response.status_code == 200:
        print(response.json()["documented_code"])
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    main()