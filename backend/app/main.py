from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from backend.app.llm_client import query_gemini
from backend.app.tts_murf import tts_generate

# ---- Import personas ----
# from backend.app.personas.friend import FriendlyAssistant
# from backend.app.personas.motivator import RecruiterPersona
# from backend.app.personas.tutor import TutorPersona


app = FastAPI()

# ---- Persona registry ----
# PERSONAS = {
#     "friend": FriendlyAssistant(),
#     "recruiter": RecruiterPersona(),
#     "tutor": TutorPersona()
# }


# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        persona = PERSONAS.get(persona_key, PERSONAS["friendly"])

    except Exception:
        raw = await request.body()
        user_text = raw.decode("utf-8").strip()
        persona = PERSONAS["friendly"]

    if not user_text:
        return JSONResponse({"error": "No message received"}, status_code=400)

    try:
        print(f"User text: {user_text}")
        print(f"Using persona: {persona.name}")

        # ---- LLM Response with persona ----
        llm_response = await run_in_threadpool(query_gemini, user_text, persona_key)
        print("AI:", llm_response)

        # ---- TTS Generation with persona voice ----
        filename = await run_in_threadpool(tts_generate, llm_response, persona)
        print("Generated audio:", filename)

        return JSONResponse({
            "persona": persona.name,
            "text": llm_response,
            "audio_url": f"/audio/{filename}"
        })

    except Exception as e:
        print("Error in /speak:", e)
        return JSONResponse({"error": str(e)}, status_code=500)
