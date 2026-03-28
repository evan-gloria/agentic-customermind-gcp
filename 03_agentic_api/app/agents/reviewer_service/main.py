# agents/reviewer_service/main.py
from fastapi import FastAPI
from vertexai.generative_models import GenerativeModel

app = FastAPI()

@app.post("/api/v1/review")
async def review_strategy(data: dict):
    strategy = data.get("strategy")
    brief = data.get("persona_brief")
    
    instruction = (
        "You are a Strict Quality Auditor. Compare the Strategy against the Persona Brief.\n"
        "1. Budget Check: Is the deal price appropriate for the customer's income?\n"
        "2. Relevance Check: Does the deal actually solve a problem for this persona?\n"
        "Output a 'PASS' or 'FAIL' grade with a 1-sentence justification."
    )
    
    model = GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(f"BRIEF: {brief}\n\nSTRATEGY: {strategy}")
    
    return {"audit_results": response.text}