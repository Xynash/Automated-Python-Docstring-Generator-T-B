from app.core.ai_docstring_engine import client, MODEL

def chat_with_code(messages: list, code: str, doc_results: str = None, review_results: dict = None) -> str:
    """
    Chat with AI about the uploaded code and all generated results.
    """
    if not client:
        raise Exception("AI Client is not initialized.")

    # Build context from everything generated so far
    context = f"UPLOADED CODE:\n{code}\n"

    if doc_results:
        context += f"\nGENERATED DOCSTRINGS:\n{doc_results}\n"

    if review_results:
        context += "\nCODE REVIEW RESULTS:\n"
        for bug in review_results.get("bugs", []):
            context += f"Bug at line {bug['line']}: {bug['issue']}\n"
        for sec in review_results.get("security", []):
            context += f"Security issue at line {sec['line']}: {sec['issue']}\n"
        for perf in review_results.get("performance", []):
            context += f"Performance issue at line {perf['line']}: {perf['issue']}\n"
        for bp in review_results.get("best_practices", []):
            context += f"Best practice issue at line {bp['line']}: {bp['issue']}\n"

    system_prompt = f"""You are an expert code assistant. 
You have full knowledge of the following code and all analysis done on it:

{context}

Answer questions about this code clearly and helpfully.
Be specific and reference actual code when relevant.
Keep answers concise but complete."""

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            temperature=0.3,
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Groq API Error: {str(e)}")