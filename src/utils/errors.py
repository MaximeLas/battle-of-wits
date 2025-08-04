"""Custom exceptions and error handling for Battle of Wits."""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCategory(str, Enum):
    """Categories of errors for better debugging."""
    CONFIGURATION = "configuration"
    API_CONNECTION = "api_connection"
    API_QUOTA = "api_quota"
    API_AUTHENTICATION = "api_authentication"
    DEBATE_LOGIC = "debate_logic"
    AUDIO_PROCESSING = "audio_processing"
    UI_ERROR = "ui_error"
    UNKNOWN = "unknown"


class BattleOfWitsError(Exception):
    """Base exception for Battle of Wits application."""
    
    def __init__(
        self, 
        message: str, 
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        user_message: Optional[str] = None,
        suggestions: Optional[list] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.user_message = user_message or message
        self.suggestions = suggestions or []
        self.context = context or {}
    
    def get_user_friendly_message(self) -> str:
        """Get a user-friendly error message with suggestions."""
        msg = f"❌ {self.user_message}"
        
        if self.suggestions:
            msg += "\n\n💡 Suggestions:"
            for suggestion in self.suggestions:
                msg += f"\n  • {suggestion}"
        
        return msg


class ConfigurationError(BattleOfWitsError):
    """Errors related to configuration and setup."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.CONFIGURATION, **kwargs)


class APIConnectionError(BattleOfWitsError):
    """Errors related to API connectivity issues."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.API_CONNECTION, **kwargs)


class APIAuthenticationError(BattleOfWitsError):
    """Errors related to API authentication."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.API_AUTHENTICATION, **kwargs)


class APIQuotaError(BattleOfWitsError):
    """Errors related to API usage limits."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.API_QUOTA, **kwargs)


class DebateLogicError(BattleOfWitsError):
    """Errors related to debate logic and flow."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.DEBATE_LOGIC, **kwargs)


class AudioProcessingError(BattleOfWitsError):
    """Errors related to audio generation and processing."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.AUDIO_PROCESSING, **kwargs)


def categorize_openai_error(error: Exception) -> BattleOfWitsError:
    """Convert OpenAI API errors into our custom error types."""
    error_str = str(error).lower()
    
    # API Key issues
    if "api" in error_str and ("key" in error_str or "auth" in error_str):
        return APIAuthenticationError(
            f"OpenAI API authentication failed: {error}",
            user_message="Invalid or missing OpenAI API key",
            suggestions=[
                "Check that your .env file exists and contains OPENAI_API_KEY",
                "Verify your API key is valid at https://platform.openai.com/api-keys",
                "Make sure there are no extra spaces in your API key"
            ],
            context={"original_error": str(error)}
        )
    
    # Rate limiting / quota issues
    if "quota" in error_str or "rate" in error_str or "limit" in error_str:
        return APIQuotaError(
            f"OpenAI API quota/rate limit exceeded: {error}",
            user_message="OpenAI API usage limit reached",
            suggestions=[
                "Check your OpenAI account usage at https://platform.openai.com/usage",
                "Wait a few minutes and try again",
                "Consider upgrading your OpenAI plan for higher limits"
            ],
            context={"original_error": str(error)}
        )
    
    # Connection issues
    if "connection" in error_str or "network" in error_str or "timeout" in error_str:
        return APIConnectionError(
            f"OpenAI API connection failed: {error}",
            user_message="Failed to connect to OpenAI API",
            suggestions=[
                "Check your internet connection",
                "Try again in a few moments",
                "Check if OpenAI services are operational at https://status.openai.com"
            ],
            context={"original_error": str(error)}
        )
    
    # Generic API error
    return BattleOfWitsError(
        f"OpenAI API error: {error}",
        category=ErrorCategory.API_CONNECTION,
        user_message="OpenAI API error occurred",
        suggestions=["Try again in a few moments"],
        context={"original_error": str(error)}
    )