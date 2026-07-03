import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from markitdown import MarkItDown

app = FastAPI(title="Self-Hosted MarkItDown Service")

# Allow communications from your Express Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MarkItDown converter once
md = MarkItDown()

@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    # Extract extension from original filename to let MarkItDown match the converter
    _, ext = os.path.splitext(file.filename or "")
    
    # Create a safe, unique temporary file preserving the extension
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
        temp_path = temp_file.name
        try:
            # Write uploaded content to temp file chunk-by-chunk to avoid high memory spikes
            shutil.copyfileobj(file.file, temp_file)
            temp_file.flush()
            temp_file.close() # Close file handle so markitdown can open it
            
            # Execute conversion
            result = md.convert(temp_path)
            return {"markdown": result.text_content}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MarkItDown Error: {str(e)}")
            
        finally:
            # Clean up the file securely
            if os.path.exists(temp_path):
                os.remove(temp_path)
