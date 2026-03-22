import sys
import os
import time
import psutil  # Performance Telemetry
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.core.parser import extract_functions
from app.core.ai_engine import analyze_function
from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring
from app.core.ai_docstring_engine import (
    generate_ai_docstring, 
    generate_structured_review, 
    generate_project_readme
)

# --- OMNIDOC AI: UNIVERSAL GATEWAY CONFIGURATION ---
app = FastAPI(
    title=" Docgen : Universal AI Code-Intelligence Platform",
    description="Multi-language asynchronous gateway for AI Documentation, Code Review, and Project Synthesis.",
    version="4.0.0"
)

# --- PRODUCTION REQUEST SCHEMA ---
class CodeRequest(BaseModel):
    code: str = Field(..., description="The source code to be processed.")
    style: Optional[str] = Field("google", description="Documentation style: google, numpy, sphinx, javadoc, jsdoc.")
    task: str = Field("document", description="The task to perform: document, review, or readme.")
    language: str = Field("python", description="Source language: python, java, javascript, cpp.")

# Helper to track RAM Usage for Operational Telemetry
def get_memory_usage():
    process = psutil.Process(os.getpid())
    return round(process.memory_info().rss / (1024 * 1024), 2)  # Returns MB

@app.get("/")
def health_check():
    """Service Health & Capability Discovery"""
    return {
        "status": "active",
        "platform": "OmniDoc AI",
        "version": "4.0.0",
        "capabilities": ["Polyglot DocGen", "Structured Review", "README Synthesis", "RAM Telemetry"]
    }

@app.post("/process")
async def process_code_endpoint(request: CodeRequest):
    """Unified Entry Point for all Code Intelligence Tasks"""
    start_time = time.perf_counter() 
    start_mem = get_memory_usage()
    
    try:
        source_code = request.code
        task = request.task.lower()
        lang = request.language.lower()
        
        # --- 1. POLYGLOT ROUTER (Universal Logic) ---
        # If language is NOT Python, bypass AST and use Direct Logic-Aware Synthesis
        if lang != "python":
            if task == "review":
                result = generate_structured_review(source_code)
            elif task == "readme":
                result = generate_project_readme(source_code)
            else:
                # Direct AI analysis for Java/JS/C++
                result = generate_ai_docstring({"full_code": source_code, "name": "Universal_Module"}, request.style)
            
            execution_time = round(time.perf_counter() - start_time, 4)
            return {
                "status": "success",
                "language": lang,
                "task": task,
                "output": result,
                "telemetry": {
                    "execution_time_sec": execution_time,
                    "memory_consumed_mb": round(get_memory_usage() - start_mem, 4)
                }
            }

        # --- 2. PYTHON README TASK ---
        if task == "readme":
            readme_content = generate_project_readme(source_code)
            execution_time = round(time.perf_counter() - start_time, 4)
            return {
                "status": "success",
                "task": "readme",
                "content": readme_content,
                "telemetry": {"execution_time_sec": execution_time}
            }

        # --- 3. PYTHON REVIEW TASK ---
        if task == "review":
            review_results = generate_structured_review(source_code)
            execution_time = round(time.perf_counter() - start_time, 4)
            return {
                "status": "success",
                "task": "review",
                "data": review_results,
                "telemetry": {"execution_time_sec": execution_time}
            }

        # --- 4. PYTHON DOCUMENTATION TASK (Core AST Logic) ---
        functions = extract_functions(source_code)
        updated_code = source_code
        doc_count = 0

        if not functions:
            return {"documented_code": source_code, "info": "No functions detected in provided Python code."}

        for func in functions:
            if func["docstring"]: continue
            metadata = analyze_function(func["node"], class_name=func["class_name"])
            try:
                # Real-time LLM Orchestration
                doc = generate_ai_docstring(metadata, request.style)
            except Exception:
                # Defensive Heuristic Fallback
                doc = generate_docstring(metadata, request.style)
            
            updated_code = insert_docstring(updated_code, metadata, doc)
            doc_count += 1
            
        execution_time = round(time.perf_counter() - start_time, 4)
        return {
            "status": "success",
            "task": "documentation",
            "documented_code": updated_code,
            "telemetry": {
                "functions_processed": doc_count,
                "execution_time_sec": execution_time,
                "memory_used_mb": round(get_memory_usage() - start_mem, 4),
                "language": "python"
            }
        }

    except Exception as e:
        # Global Exception Handler
        raise HTTPException(status_code=500, detail=f"OmniDoc Engine Error: {str(e)}")