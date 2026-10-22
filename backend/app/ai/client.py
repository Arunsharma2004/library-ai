"""The ONLY file that talks to the AI provider.

Every AI feature calls ask(). To switch provider (Anthropic, Ollama, ...), change
this file and the .env settings. Nothing else in the app needs to change.
"""
import logging
from functools import lru_cache

from app.config import settings

logger = logging.getLogger(__name__)


class AIError(Exception):
    """The AI is not configured or could not answer. The message is safe to show users."""


@lru_cache
def _client():
    # Imported here so the rest of the app still starts if the package is missing.
    from google import genai

    return genai.Client(api_key=settings.GEMINI_API_KEY)


def ask(prompt: str, system: str | None = None) -> str:
    """Sends one prompt and returns the answer as plain text."""
    if not settings.GEMINI_API_KEY:
        raise AIError("AI is not configured. Add GEMINI_API_KEY to backend/.env")

    # One text input: our instructions first, then the actual request.
    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    try:
        interaction = _client().interactions.create(
            model=settings.GEMINI_MODEL,
            input=full_prompt,
        )
        text = interaction.output_text
    except Exception as error:
        # Log the real error for us, but show the user only a safe message.
        logger.exception("AI request failed")
        raise AIError("The AI service could not answer right now. Please try again.") from error

    if not text or not text.strip():
        raise AIError("The AI returned an empty answer.")
    return text.strip()