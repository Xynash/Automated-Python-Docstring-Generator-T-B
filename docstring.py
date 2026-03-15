
import re
import sys
import os


def generate_docs(code, language):

    docs = []

    functions = re.findall(r'(int|float|double|void|char|bool|string)?\s*(\w+)\((.*?)\)', code)

    for return_type, func_name, params in functions:

        param_list = []
        if params.strip():
            for p in params.split(","):
                name = p.strip().split(" ")[-1]
                param_list.append(name)

        # Python style
        if language == "py":

            doc = '"""\n'
            doc += f"{func_name} function\n"
            doc += '"""\n'


        # C / C++ / Java / JS style
        else:

            doc = "/**\n"
            doc += f" * {func_name} function\n"

            for p in param_list:
                doc += f" * @param {p}\n"

            if return_type and return_type != "void":
                doc += " * @return value\n"

            doc += " */\n"

        docs.append(doc + f"{func_name}({params})\n")

    return "\n".join(docs)


if len(sys.argv) < 2:
    print("Usage: python docstring.py <file>")
    sys.exit()


file = sys.argv[1]

if not os.path.exists(file):
    print("File not found")
    sys.exit()


language = file.split(".")[-1]

with open(file, "r", encoding="utf-8") as f:
    code = f.read()


result = generate_docs(code, language)

print("\nLanguage detected:", language)
print("\nGenerated Documentation:\n")
print(result)

