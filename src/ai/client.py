"""OpenAI client wrapper with comprehensive error handling."""

import os
from typing import Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

from ..utils.logger import get_logger
from ..utils.errors import (
    ConfigurationError, 
    APIAuthenticationError,
    categorize_openai_error
)

# Load environment variables
load_dotenv()
logger = get_logger()


class OpenAIClient:
    """Wrapper around OpenAI client with comprehensive error handling."""
    
    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
        self._validate_and_initialize()
    
    def _validate_and_initialize(self) -> None:
        """Validate configuration and initialize the OpenAI client."""
        logger.info("Initializing OpenAI client")
        
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.error("OpenAI API key not found in environment")
            raise ConfigurationError(
                "OpenAI API key not found in environment variables",
                user_message="OpenAI API key is missing",
                suggestions=[
                    "Create a .env file in your project root",
                    "Add OPENAI_API_KEY=your_api_key_here to the .env file",
                    "Copy .env.example to .env and edit it with your key",
                    "Get your API key from https://platform.openai.com/api-keys"
                ],
                context={"env_file_exists": os.path.exists(".env")}
            )
        
        if not api_key.startswith("sk-"):
            logger.error("Invalid OpenAI API key format", api_key_prefix=api_key[:10])
            raise ConfigurationError(
                "Invalid OpenAI API key format",
                user_message="OpenAI API key appears to be invalid",
                suggestions=[
                    "API keys should start with 'sk-'",
                    "Check for extra spaces or characters in your .env file",
                    "Get a new API key from https://platform.openai.com/api-keys"
                ]
            )
        
        try:
            self._client = AsyncOpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize OpenAI client", error=e)
            raise categorize_openai_error(e)
    
    @property
    def client(self) -> AsyncOpenAI:
        """Get the OpenAI client instance."""
        if self._client is None:
            self._validate_and_initialize()
        return self._client
    
    async def create_chat_completion(self, **kwargs):
        """Create a chat completion with comprehensive error handling."""
        logger.debug("Creating chat completion", model=kwargs.get('model'), messages_count=len(kwargs.get('messages', [])))
        
        try:
            response = await self.client.chat.completions.create(**kwargs)
            logger.info("Chat completion successful", 
                       model=kwargs.get('model'), 
                       tokens_used=response.usage.total_tokens if response.usage else 'unknown')
            return response
            
        except Exception as e:
            logger.error("Chat completion failed", 
                        error=e, 
                        model=kwargs.get('model'),
                        message_count=len(kwargs.get('messages', [])))
            raise categorize_openai_error(e)
    
    async def create_speech(self, **kwargs):
        """Create speech with comprehensive error handling."""
        logger.debug("Creating speech", 
                    model=kwargs.get('model'), 
                    voice=kwargs.get('voice'),
                    text_length=len(kwargs.get('input', '')))
        
        try:
            response = await self.client.audio.speech.create(**kwargs)
            logger.info("Speech generation successful", 
                       model=kwargs.get('model'),
                       voice=kwargs.get('voice'))
            return response
            
        except Exception as e:
            logger.error("Speech generation failed", 
                        error=e,
                        model=kwargs.get('model'),
                        voice=kwargs.get('voice'))
            raise categorize_openai_error(e)
    
    async def test_connection(self) -> bool:
        """Test the OpenAI API connection."""
        logger.info("Testing OpenAI API connection")
        
        try:
            # Simple test request
            response = await self.create_chat_completion(
                model="gpt-4o-mini",  # Use cheaper model for testing
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            logger.info("API connection test successful")
            return True
            
        except Exception as e:
            logger.error("API connection test failed", error=e)
            return False


# Global client instance
_openai_client = None

def get_openai_client() -> OpenAIClient:
    """Get the global OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client