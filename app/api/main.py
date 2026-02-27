import sys
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field  # <--- This was the missing line!
from app.core.parser import extract_functions
from app.core.ai_engine import analyze_function
from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring
from app.core.ai_docstring_engine import generate_ai_docstring

app = FastAPI(title="Advanced AI Docstring Generator API")

# Define the Request Schema
class CodeRequest(BaseModel):
    code: str
    style: Optional[str] = "google" # Default style is google

@app.get("/")
def health_check():
    return {"status": "active", "message": "The Docstring Generator API is online."}

@app.post("/generate")
async def generate_code_endpoint(request: CodeRequest):
    try:
        source_code = request.code
        style = request.style
        
        # Step A: Parse functions
        functions = extract_functions(source_code)
        updated_code = source_code
        
        if not functions:
            return {"documented_code": source_code, "info": "No functions detected."}

        # Step B: Process each function
        for func in functions:
            if func["docstring"]: # Skip if already has one
                continue
            
            # Extract metadata
            metadata = analyze_function(func["node"], class_name=func["class_name"])
            
            # Step C: Generate docstring using AI with style preference
            try:
                # We pass 'style' to the AI engine now
                docstring = generate_ai_docstring(metadata, style)
                print(f"✅ AI ({style}): Generated for {metadata['name']}")
            except Exception as e:
                print(f"⚠️ AI Failed, using fallback: {e}")
                docstring = generate_docstring(metadata)
            
            # Step D: Insert back into code
            updated_code = insert_docstring(updated_code, metadata, docstring)
            
        return {
            "status": "success",
            "style_applied": style,
            "documented_code": updated_code
        }

    except Exception as e:
        print(f"🔥 Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))