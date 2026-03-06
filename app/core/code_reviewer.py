from app.core.ai_docstring_engine import client, MODEL

def review_code(code: str) -> dict:
    """
    Reviews code and returns bugs, security issues,
    performance tips and best practices with line numbers,
    problematic code and fixed code snippets.
    """
    if not client:
        raise Exception("AI Client is not initialized.")

    prompt = f"""You are an expert code reviewer.
Analyze the following code carefully.
CRITICAL RULES:
- Use EXACTLY "- LINE: X | CODE: Y | ISSUE: Z | FIX: W" format
- Each section MUST have at least one item
- If no real bugs exist still suggest defensive coding improvements
- Never write "None found"
- Never skip any section
- Do NOT include any summary or explanation outside the sections
CODE TO REVIEW:
{code}

You MUST respond in EXACTLY this format for each issue.
Each issue MUST be on a single line starting with "- ":

BUGS:
- LINE: 5 | CODE: x = int(input()) | ISSUE: No input validation | FIX: x = int(input()) if input().isdigit() else 0

SECURITY:
- LINE: 10 | CODE: query = "SELECT * FROM users WHERE id=" + id | ISSUE: SQL injection vulnerability | FIX: query = "SELECT * FROM users WHERE id=?" , (id,)

PERFORMANCE:
- LINE: 15 | CODE: for i in range(len(lst)) | ISSUE: Inefficient iteration | FIX: for item in lst

BEST PRACTICES:
- LINE: 20 | CODE: def f(x) | ISSUE: Poor function naming | FIX: def calculate_total(value)

SUMMARY:
Write one paragraph summary here.

"""

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software engineer doing a professional code review. Be specific, practical and always show code examples."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        raw = completion.choices[0].message.content.strip()
        return parse_review(raw)

    except Exception as e:
        raise Exception(f"Groq API Error: {str(e)}")

def parse_review_item(line: str) -> dict:
    """
    Parses a single review line into line number,
    problematic code, issue and fix.
    """
    item = {
        "line": "N/A",
        "code": "N/A",
        "issue": line[2:],  # fallback: use full line as issue
        "fix": "N/A"
    }

    try:
        content = line[2:]  # remove "- " prefix
        parts = content.split(" | ")
        
        for part in parts:
            part = part.strip()
            if "LINE:" in part:
                item["line"] = part.split("LINE:")[-1].strip()
            elif "CODE:" in part:
                item["code"] = part.split("CODE:")[-1].strip()
            elif "ISSUE:" in part:
                item["issue"] = part.split("ISSUE:")[-1].strip()
            elif "FIX:" in part:
                item["fix"] = part.split("FIX:")[-1].strip()
    except:
        pass

    return item




def parse_review(raw: str) -> dict:
    """
    Parses the raw AI review into a structured dictionary.
    """
    sections = {
        "bugs": [],
        "security": [],
        "performance": [],
        "best_practices": [],
        "summary": ""
    }

    current_section = None
    lines = raw.split("\n")

    for line in lines:
        line = line.strip()
        if line.startswith("BUGS:"):
            current_section = "bugs"
        elif line.startswith("SECURITY:"):
            current_section = "security"
        elif line.startswith("PERFORMANCE:"):
            current_section = "performance"
        elif line.startswith("BEST PRACTICES:"):
            current_section = "best_practices"
        elif line.startswith("SUMMARY:"):
            current_section = "summary"
        elif line.startswith("- ") and current_section in ["bugs", "security", "performance", "best_practices"]:
            sections[current_section].append(parse_review_item(line))
        elif current_section == "summary" and line:
            sections["summary"] += line + " "

    return sections