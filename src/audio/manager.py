"""Audio manager for TTS generation and streaming."""

import asyncio
from typing import Optional
from io import BytesIO
from ..debate.models import DebateConfig
from ..ai.client import get_openai_client


class AudioManager:
    """Manages TTS generation and audio streaming for debates."""
    
    def __init__(self, config: DebateConfig):
        self.config = config
        self.client = get_openai_client()
    
    async def generate_audio(self, text: str, voice: str) -> bytes:
        """Generate audio from text using OpenAI TTS."""
        try:
            response = await self.client.create_speech(
                model="tts-1",  # Using faster model for real-time feel
                voice=voice,
                input=text,
                speed=self.config.tts_speed
            )
            
            # The response content is the audio data
            return response.content
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            # Return empty bytes on error
            return b''
    
    async def generate_audio_stream(self, text: str, voice: str, chunk_size: int = 1024):
        """Generate audio in chunks for streaming (future enhancement)."""
        # This would be used for real-time streaming of audio as it's generated
        # For now, we'll keep it simple and generate the full audio
        audio_data = await self.generate_audio(text, voice)
        
        # Yield chunks of the audio data
        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i:i + chunk_size]