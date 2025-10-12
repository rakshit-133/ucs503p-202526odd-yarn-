# backend/main.py

import base64
from io import BytesIO
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import all the necessary functions and classes from your analyzer script
from analyzer import generate_ai_summary, CodeAnalyzer, build_graph_model, create_logic_flowchart, ast

# Initialize the FastAPI app
app = FastAPI()

# --- CORS Configuration ---
# This block fixes the "blocked by CORS policy" error.
# In backend/main.py

origins = [
    "http://localhost:5176", # Add this new line
    "http://localhost:5173",
    "http://localhost:3000",
]

# ... (the rest of the middleware code)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Data Models ---
class CodePayload(BaseModel):
    code: str

class AnalysisResult(BaseModel):
    summary: str
    flowchart_base64: str | None
    error: str | None

# --- API Endpoint ---
@app.post("/analyze", response_model=AnalysisResult)
async def analyze_code_endpoint(payload: CodePayload):
    try:
        # 1. Generate the AI-powered natural language summary
        summary = generate_ai_summary(payload.code)

        # 2. Parse the code to generate the flowchart
        tree = ast.parse(payload.code)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        code_structure = analyzer.structure
        
        graph_model = build_graph_model(code_structure)
        dot_obj = create_logic_flowchart(graph_model)
        
        # 3. Convert the flowchart object to a Base64 image string
        img_buffer = BytesIO(dot_obj.pipe(format='png'))
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        
        # 4. Return the successful result
        return AnalysisResult(summary=summary, flowchart_base64=img_base64, error=None)

    except SyntaxError as e:
        return AnalysisResult(summary="", flowchart_base64=None, error=f"Syntax Error in provided code: {e}")