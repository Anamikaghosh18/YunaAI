from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from backend.app.route.auth import router as auth_router
from backend.app.models import Base
from backend.app.database import engine
from backend.app.llm_client import query_gemini
from backend.app.tts_murf import tts_generate


app = FastAPI()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Register auth router ----
app.include_router(auth_router, prefix="/auth", tags=["auth"])


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent.parent / "frontend"
STATIC_AUDIO_DIR = BASE_DIR / "static/audio"
STATIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# ---- Static Files ----
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")
app.mount("/audio", StaticFiles(directory=STATIC_AUDIO_DIR), name="audio")


@app.get("/")
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/speak")
async def speak_endpoint(request: Request):
    """
    User sends:
    {
        "text": "Hello",
        "persona": "friendly"
    }
    """
    try:
        body = await request.json()
        user_text = body.get("text", "").strip()
        persona_key = body.get("persona", "friendly")  # default persona

    except Exception:
        raw = await request.body()
        user_text = raw.decode("utf-8").strip()
        persona_key = "friendly"

    if not user_text:
        return JSONResponse({"error": "No message received"}, status_code=400)

    try:
        print(f"User text: {user_text}")
        print(f"Using persona: {persona_key}")

        # ---- LLM Response with persona ----
        llm_response = await run_in_threadpool(query_gemini, user_text, persona_key)
        print("AI:", llm_response)

        # ---- TTS Generation ----
        filename = await run_in_threadpool(tts_generate, llm_response)
        print("Generated audio:", filename)

        return JSONResponse({
            "persona": persona_key,
            "text": llm_response,
            "audio_url": f"/audio/{filename}"
        })

    except Exception as e:
        print("Error in /speak:", e)
        return JSONResponse({"error": str(e)}, status_code=500)
