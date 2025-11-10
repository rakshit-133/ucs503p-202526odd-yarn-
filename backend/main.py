import base64
from io import BytesIO
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

# Import all the necessary functions and classes from your analyzer script
from analyzer import generate_ai_summary, CodeAnalyzer, build_graph_model, create_logic_flowchart, ast

# Initialize the FastAPI app
app = FastAPI()

# --- CORS Configuration ---
frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

origins = [
    "http://localhost:5176",
    "http://localhost:5173",
    "http://localhost:3000",
    frontend_url  # This adds your live URL
]

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
def analyze_code_endpoint(payload: CodePayload):
    """
    Analyzes a piece of Python code to generate a summary and a flowchart.
    This is a synchronous endpoint because it performs CPU/IO-bound tasks.
    """
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
        
        if dot_obj is None:
             raise ValueError("Failed to generate flowchart object from the graph model.")
        
        # 3. Convert the flowchart object to a Base64 image string
        png_data = dot_obj.pipe(format='png')
        if not png_data:
            raise RuntimeError("Graphviz returned empty data. Is it installed and in your system's PATH?")
            
        img_buffer = BytesIO(png_data)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        
        # 4. Return the successful result
        return AnalysisResult(summary=summary, flowchart_base64=img_base64, error=None)

    except Exception as e:
        # Catch any error during the process (Syntax, Network, Graphviz, etc.)
        # and return a structured error message.
        return AnalysisResult(summary="", flowchart_base64=None, error=f"An unexpected error occurred: {e}")