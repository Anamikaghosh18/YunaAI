from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from pathlib import Path
from backend.app.llm_client import query_gemini
from backend.app.tts_murf import tts_generate
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware at the top
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, OPTIONS, GET, etc.
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent.parent / "frontend"
STATIC_AUDIO_DIR = BASE_DIR / "static/audio"
STATIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Serve frontend static files (JS, CSS, images)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")
app.mount("/audio", StaticFiles(directory=STATIC_AUDIO_DIR), name="audio")

# Serve index.html
@app.get("/")
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.post("/speak")
async def speak_endpoint(request: Request):
    try:
        body = await request.json()
        user_text = body.get("text", "").strip()
    except Exception:
        raw = await request.body()
        user_text = raw.decode("utf-8").strip()

    if not user_text:
        return JSONResponse({"error": "No message received"}, status_code=400)

    try:
        print("User text received:", user_text)

        # Query Gemini
        llm_response = await run_in_threadpool(query_gemini, user_text)
        print("LLM response:", llm_response)

        # Generate TTS
        filename = await run_in_threadpool(tts_generate, llm_response)
        print("Generated audio filename:", filename)

        return JSONResponse({
            "text": llm_response,
            "audio_url": f"/audio/{filename}"
        })
    except Exception as e:
        print("Error in /speak:", e)
        return JSONResponse({"error": str(e)}, status_code=500)
