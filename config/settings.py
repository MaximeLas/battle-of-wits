"""Application settings and configuration."""

import os
from typing import Dict, Any

# Default settings
DEFAULT_SETTINGS: Dict[str, Any] = {
    # OpenAI Configuration
    "default_chat_model": os.getenv("DEFAULT_CHAT_MODEL", "gpt-4o"),
    "default_tts_model": os.getenv("DEFAULT_TTS_MODEL", "tts-1"),
    "default_tts_voice": os.getenv("DEFAULT_TTS_VOICE", "alloy"),
    
    # Debate Configuration
    "max_response_tokens": 500,
    "default_temperature": 0.7,
    "default_max_turns": 8,
    
    # UI Configuration  
    "page_title": "Battle of Wits",
    "page_icon": "🥊",
    
    # Audio Configuration
    "audio_format": "mp3",
    "default_speech_speed": 1.0,
    
    # Available voices for TTS
    "available_voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
    
    # Available models
    "available_models": ["gpt-4o", "gpt-4o-mini"]
}


def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting value."""
    return DEFAULT_SETTINGS.get(key, default)


def update_setting(key: str, value: Any) -> None:
    """Update a setting value."""
    DEFAULT_SETTINGS[key] = value