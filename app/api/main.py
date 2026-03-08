import sys
import os
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.core.parser import extract_functions
from app.core.ai_engine import analyze_function
from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring
# Import both the docstring engine and the new structured reviewer
from app.core.ai_docstring_engine import generate_ai_docstring, generate_structured_review

app = FastAPI(
    title="PyDoc AI: Unified Multi-Service Gateway",
    version="3.0.0"
)

# --- MILESTONE 3: UNIFIED REQUEST SCHEMA ---
class CodeRequest(BaseModel):
    code: str
    style: Optional[str] = "google"
    task: str = "document"  # New: Options are "document" or "review"
    language: str = "python" # To support Member 4's Java/C++ expansion

@app.get("/")
def health_check():
    return {
        "status": "active",
        "version": "Milestone 3",
        "services": ["Documentation", "Code Review", "Telemetry"]
    }

@app.post("/process")
async def process_code_endpoint(request: CodeRequest):
    # --- FEATURE: SYSTEM PERFORMANCE TELEMETRY ---
    start_time = time.perf_counter() 
    
    try:
        source_code = request.code
        task = request.task.lower()
        
        # --- FEATURE: UNIFIED TASK GATEWAY (Switching Logic) ---
        
        # TASK 1: CODE REVIEW (Member 2's Logic)
        if task == "review":
            # This calls the Structured JSON Orchestration logic
            review_results = generate_structured_review(source_code)
            execution_time = round(time.perf_counter() - start_time, 4)
            
            return {
                "status": "success",
                "task": "review",
                "data": review_results,
                "telemetry": {
                    "execution_time_sec": execution_time,
                    "model": "Llama-3.3-70B"
                }
            }

        # TASK 2: DOCUMENTATION (Existing Core Logic)
        else:
            functions = extract_functions(source_code)
            updated_code = source_code
            doc_count = 0

            if not functions:
                return {"documented_code": source_code, "info": "No functions detected."}

            for func in functions:
                if func["docstring"]: continue
                
                metadata = analyze_function(func["node"], class_name=func["class_name"])
                
                try:
                    docstring = generate_ai_docstring(metadata, request.style)
                except Exception as e:
                    print(f"⚠️ AI DocGen Fallback: {e}")
                    docstring = generate_docstring(metadata)
                
                updated_code = insert_docstring(updated_code, metadata, docstring)
                doc_count += 1
            
            execution_time = round(time.perf_counter() - start_time, 4)
            
            return {
                "status": "success",
                "task": "documentation",
                "documented_code": updated_code,
                "telemetry": {
                    "functions_processed": doc_count,
                    "execution_time_sec": execution_time,
                    "language": request.language
                }
            }

    except Exception as e:
        print(f"🔥 Gateway Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))