from .tutor import TUTOR_PROMPT
from .friend import FRIEND_PROMPT
from .motivator import MOTIVATOR_PROMPT

PERSONAS = {
    "tutor": TUTOR_PROMPT,
    "friend": FRIEND_PROMPT,
    "motivator": MOTIVATOR_PROMPT
}


def get_persona_prompt(persona_name: str) -> str:
    return PERSONAS.get(persona_name.lower(), "You are a helpful AI assistant.")
