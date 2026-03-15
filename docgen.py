
import requests
import argparse
import os

API_URL = "http://127.0.0.1:8000/process"

def main():
    parser = argparse.ArgumentParser(description="Docstring Generator CLI")
    parser.add_argument("file", help="Path to source file")
    parser.add_argument("--style", default="google",
                        help="Docstring style (google/numpy/sphinx)")
    
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print("❌ File not found.")
        return

    # Language detection
    if args.file.endswith(".py"):
        language = "python"
    elif args.file.endswith(".java"):
        language = "java"
    else:
        print("❌ Unsupported file type")
        return

    with open(args.file, "r") as f:
        code = f.read()

    response = requests.post(API_URL, json={
        "code": code,
        "style": args.style,
        "language": language
    })

    if response.status_code == 200:
        data = response.json()

        if "documented_code" in data:
            result = data["documented_code"]

        elif "output" in data:
            result = data["output"]

        else:
            print("⚠ Unexpected API response:", data)
            return

        print("\n✅ Generated Documentation:\n")
        print(result)

    else:
        print("❌ API Error:", response.text)


if __name__ == "__main__":
    main()

