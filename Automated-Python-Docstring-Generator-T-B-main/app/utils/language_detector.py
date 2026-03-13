def detect_language(filename):

    if filename.endswith(".py"):
        return "Python"

    elif filename.endswith(".java"):
        return "Java"

    elif filename.endswith(".c"):
        return "C"

    elif filename.endswith(".cpp"):
        return "C++"

    else:
        return "Unknown"