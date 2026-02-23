from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.parser import extract_functions
from app.core.ai_engine import analyze_function
from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring

# 1. Initialize the FastAPI app
app = FastAPI(title="AI Docstring Generator API")

# 2. Define the Request Schema (What the API expects)
class CodeRequest(BaseModel):
    code: str

# 3. Simple health check endpoint
@app.get("/")
def health_check():
    return {"status": "active", "message": "The Docstring Generator API is online."}

# 4. The main endpoint for generating docstrings
@app.post("/generate")
async def generate_code_endpoint(request: CodeRequest):
    try:
        source_code = request.code
        
        # Run your existing Pipeline
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
            
            # Generate docstring (Heuristic mode for now)
            docstring = generate_docstring(metadata)
            
            # Insert back into code
            updated_code = insert_docstring(updated_code, metadata, docstring)
            
        # Return the final result
        return {
            "status": "success",
            "documented_code": updated_code
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")