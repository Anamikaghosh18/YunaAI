import os

from google import genai
from google.genai import types 

def query_gemini(prompt: str) -> str:
    MODEL_NAME = "gemini-2.5-flash" 
    if not prompt or prompt.isspace():
        return "Sorry, I didn't receive any text to process. Please try again."

    try:
        client = genai.Client()
        config = types.GenerateContentConfig(
            # System instruction sets the LLM's persona/role
            system_instruction="You are a helpful and concise assistant.",
            temperature=0.7,
            max_output_tokens=200 
        )

        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )

        
        return response.text 

    except Exception as e:
        # 6. Log and return a descriptive error message on failure
        error_message = f"Gemini API error occurred: {e}"
        print(f"DEBUG: {error_message}")
        return f"I'm sorry, I encountered an internal error. {e}"

