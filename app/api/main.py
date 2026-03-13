import sys
import os
import time
import psutil  # Ensure you ran: pip install psutil
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.parser import extract_functions
from app.core.ai_engine import analyze_function
from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring
from app.core.ai_docstring_engine import (
    generate_ai_docstring, 
    generate_structured_review, 
    generate_project_readme
)

# --- THE CRITICAL LINE UVICORN NEEDS ---
app = FastAPI(
    title="PyDoc AI: Advanced Unified Platform",
    description="Multi-service gateway for Documentation, Code Review, and Project Analytics",
    version="3.1.0"
)

# --- REQUEST SCHEMA ---
class CodeRequest(BaseModel):
    code: str
    style: Optional[str] = "google"
    task: str = "document"    # document | review | readme
    language: str = "python"  # python | java | javascript | cpp

# Helper to track RAM Usage
def get_memory_usage():
    process = psutil.Process(os.getpid())
    return round(process.memory_info().rss / (1024 * 1024), 2)

@app.get("/")
def health_check():
    return {
        "status": "active",
        "version": "Milestone 3.1",
        "services": ["Documentation", "Code Review", "README Generator", "Resource Telemetry"]
    }

@app.post("/process")
async def process_code_endpoint(request: CodeRequest):
    start_time = time.perf_counter() 
    start_mem = get_memory_usage()
    
    try:
        source_code = request.code
        task = request.task.lower()
        lang = request.language.lower()
        
        # 1. Polyglot Router
        if lang != "python":
            if task == "review":
                result = generate_structured_review(source_code)
            elif task == "readme":
                result = generate_project_readme(source_code)
            else:
                result = generate_ai_docstring({"full_code": source_code, "name": "File_Logic"}, request.style)
            
            return {
                "status": "success",
                "language": lang,
                "output": result,
                "telemetry": {"execution_time_sec": round(time.perf_counter() - start_time, 4)}
            }

        # 2. README Task
        if task == "readme":
            readme_content = generate_project_readme(source_code)
            return {
                "status": "success",
                "content": readme_content,
                "telemetry": {"execution_time_sec": round(time.perf_counter() - start_time, 4)}
            }

        # 3. Review Task
        if task == "review":
            review_results = generate_structured_review(source_code)
            return {
                "status": "success",
                "data": review_results,
                "telemetry": {"execution_time_sec": round(time.perf_counter() - start_time, 4)}
            }

        # 4. Documentation Task (Python AST)
        functions = extract_functions(source_code)
        updated_code = source_code
        for func in functions:
            if func["docstring"]: continue
            metadata = analyze_function(func["node"], class_name=func["class_name"])
            try:
                doc = generate_ai_docstring(metadata, request.style)
            except:
                doc = generate_docstring(metadata, request.style)
            updated_code = insert_docstring(updated_code, metadata, doc)
            
        execution_time = round(time.perf_counter() - start_time, 4)
        return {
            "status": "success",
            "documented_code": updated_code,
            "telemetry": {
                "execution_time_sec": execution_time,
                "memory_used_mb": round(get_memory_usage() - start_mem, 4)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))