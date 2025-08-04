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
            # Calculate cost
            cost_info = ""
            if response.usage:
                model = kwargs.get('model', '')
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                
                if model == "gpt-4o":
                    input_cost = input_tokens * 0.0025 / 1000  # $2.50 per 1K input tokens
                    output_cost = output_tokens * 0.01 / 1000  # $10.00 per 1K output tokens
                elif "gpt-4o-mini" in model:
                    input_cost = input_tokens * 0.00015 / 1000  # $0.15 per 1K input tokens
                    output_cost = output_tokens * 0.0006 / 1000  # $0.60 per 1K output tokens
                else:
                    input_cost = output_cost = 0
                
                total_cost = input_cost + output_cost
                cost_info = f"${total_cost:.4f}"
            
            logger.info("Chat completion successful", 
                       model=kwargs.get('model'), 
                       input_tokens=response.usage.prompt_tokens if response.usage else 'unknown',
                       output_tokens=response.usage.completion_tokens if response.usage else 'unknown',
                       total_tokens=response.usage.total_tokens if response.usage else 'unknown',
                       estimated_cost=cost_info if cost_info else 'unknown')
            return response
            
        except Exception as e:
            logger.error("Chat completion failed", 
                        error=e, 
                        model=kwargs.get('model'),
                        message_count=len(kwargs.get('messages', [])))
            raise categorize_openai_error(e)
    
    async def create_speech(self, **kwargs):
        """Create speech with comprehensive error handling."""
        text_input = kwargs.get('input', '')
        text_length = len(text_input)
        
        logger.debug("Creating speech", 
                    model=kwargs.get('model'), 
                    voice=kwargs.get('voice'),
                    text_length=text_length)
        
        try:
            response = await self.client.audio.speech.create(**kwargs)
            
            # Calculate TTS cost based on characters (TTS pricing is per 1K characters)
            model = kwargs.get('model', '')
            if model == "tts-1":
                cost_per_1k_chars = 0.015  # $0.015 per 1K characters for tts-1
            elif model == "tts-1-hd":
                cost_per_1k_chars = 0.030  # $0.030 per 1K characters for tts-1-hd
            else:
                cost_per_1k_chars = 0.015  # Default to tts-1 pricing
            
            estimated_cost = (text_length / 1000) * cost_per_1k_chars
            
            logger.info("Speech generation successful", 
                       model=kwargs.get('model'),
                       voice=kwargs.get('voice'),
                       characters=text_length,
                       estimated_cost=f"${estimated_cost:.4f}")
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