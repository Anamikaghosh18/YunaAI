from google import genai
from google.genai import types
from .personas import get_persona_prompt  # <-- import your persona helper


def query_gemini(prompt: str, persona_name: str = "default") -> str:
    MODEL_NAME = "gemini-2.5-flash"

    if not prompt or prompt.isspace():
        return "Sorry, I didn't receive any text to process. Please try again."

    # Get persona system prompt
    persona_instruction = get_persona_prompt(persona_name)

    try:
        client = genai.Client()

        config = types.GenerateContentConfig(
            system_instruction=persona_instruction,  # persona now applied
            temperature=0.7,
            max_output_tokens=200
        )

        # Format final content structure
        full_prompt = f"User: {prompt}\nRespond in the style described."

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config=config
        )

        return response.text.strip()

    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"I'm sorry, something went wrong processing your request: {e}"
