import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
from agent import github_card_agent
# Import tools directly for fallback
from mcp_server import scrape_github, analyze_profile, generate_card_html, save_card
from pathlib import Path

app = FastAPI(title="GitHub Dev Card Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for cards
STATIC_DIR = Path(__file__).parent / "static"
CARDS_DIR = STATIC_DIR / "cards"
CARDS_DIR.mkdir(parents=True, exist_ok=True)

# Services
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

# Runner
runner = Runner(
    app_name="github-card-generator",
    agent=github_card_agent,
    session_service=session_service,
    memory_service=memory_service,
    auto_create_session=True
)

class GenerateRequest(BaseModel):
    username: str

@app.get("/")
def serve_frontend():
    return FileResponse(STATIC_DIR / "index.html")

@app.post("/generate")
async def generate_card_endpoint(request: GenerateRequest):
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    input_text = f"Generate a dev card for {username}"
    session_id = f"session_{username}"
    
    # Create the message content for ADK
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=input_text)]
    )
    
    try:
        final_response = ""
        # Try running via the Intelligent Agent first
        try:
            async for event in runner.run_async(
                user_id=username, 
                session_id=session_id, 
                new_message=content
            ):
                if event.text:
                    final_response += event.text
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                print(f"Agent Quota Exceeded. Falling back to direct tool execution for {username}...")
                # MANUAL FALLBACK (Bypass LLM Agent)
                # 1. Scrape
                data = await scrape_github(username)
                if "error" in data:
                    raise Exception(data["error"])
                
                # 2. Analyze (Analyze has its own internal fallback if Gemini fails)
                analysis = await analyze_profile(data)
                
                # 3. Generate HTML
                html = generate_card_html(username, data, analysis)
                
                # 4. Save
                save_card(username, html)
                
                final_response = "Generated using fallback mode due to API quota."
            else:
                raise e
        
        # Verify the card was created
        card_file = CARDS_DIR / f"{username}.html"
        if card_file.exists():
            with open(card_file, "r", encoding="utf-8") as f:
                card_html = f.read()
            return {
                "status": "success",
                "username": username,
                "card_url": f"/card/{username}",
                "card_html": card_html,
                "note": final_response
            }
        else:
            raise HTTPException(status_code=500, detail="Card generation failed even in fallback.")
            
    except Exception as e:
        print(f"Error in generate_card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/card/{username}", response_class=HTMLResponse)
async def get_card(username: str):
    card_file = CARDS_DIR / f"{username}.html"
    if not card_file.exists():
        raise HTTPException(status_code=404, detail="Card not found")
    
    with open(card_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "github-card-generator"}

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
