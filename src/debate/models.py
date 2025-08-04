"""Core data models for the debate system."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DebateFormat(str, Enum):
    """Available debate formats."""
    CLASSIC = "classic"
    # Future formats can be added here
    # RAPID_FIRE = "rapid_fire"
    # ROLEPLAY = "roleplay"


class DebaterRole(str, Enum):
    """Roles in the debate."""
    DEBATER_A = "debater_a"
    DEBATER_B = "debater_b"


class TurnType(str, Enum):
    """Types of debate turns."""
    OPENING = "opening"
    REBUTTAL = "rebuttal"
    CLOSING = "closing"


class TokenUsage(BaseModel):
    """Token usage information for a message."""
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    model: str = Field(default="")


class DebateMessage(BaseModel):
    """A single message in the debate."""
    role: DebaterRole
    content: str
    turn_type: TurnType
    turn_number: int
    timestamp: datetime = Field(default_factory=datetime.now)
    audio_duration: Optional[float] = None  # Duration in seconds when TTS is complete
    token_usage: Optional[TokenUsage] = None  # Token usage for this message


class DebateConfig(BaseModel):
    """Configuration for a debate session."""
    topic: str = Field(..., description="The debate topic")
    position_a: str = Field(..., description="Position that Debater A will defend")
    position_b: str = Field(..., description="Position that Debater B will defend")
    max_turns: int = Field(default=8, ge=4, le=20, description="Maximum number of turns per debater")
    format: DebateFormat = Field(default=DebateFormat.CLASSIC)
    
    # Auto-advance Configuration
    auto_advance: bool = Field(default=False, description="Automatically advance through debate turns")
    turn_delay: float = Field(default=3.0, ge=0.5, le=10.0, description="Seconds to wait between turns in auto-advance mode")
    wait_for_audio: bool = Field(default=True, description="Wait for audio to finish before advancing")
    
    # AI Configuration
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    # TTS Configuration
    tts_voice_a: str = Field(default="alloy")
    tts_voice_b: str = Field(default="echo")
    tts_speed: float = Field(default=1.0, ge=0.25, le=4.0)


class DebateState(BaseModel):
    """Current state of an ongoing debate."""
    config: DebateConfig
    messages: List[DebateMessage] = Field(default_factory=list)
    current_turn: int = Field(default=1)
    current_role: DebaterRole = Field(default=DebaterRole.DEBATER_A)
    is_active: bool = Field(default=False)
    is_complete: bool = Field(default=False)
    
    # Auto-advance state
    auto_advance_active: bool = Field(default=False)
    auto_advance_paused: bool = Field(default=False)
    last_turn_timestamp: Optional[datetime] = None
    
    # Token usage tracking
    total_input_tokens: int = Field(default=0)
    total_output_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    
    def get_current_turn_type(self) -> TurnType:
        """Determine the current turn type based on turn number."""
        if self.current_turn <= 2:
            return TurnType.OPENING
        elif self.current_turn >= self.config.max_turns - 1:
            return TurnType.CLOSING
        else:
            return TurnType.REBUTTAL
    
    def switch_debater(self) -> None:
        """Switch to the next debater."""
        if self.current_role == DebaterRole.DEBATER_A:
            self.current_role = DebaterRole.DEBATER_B
        else:
            self.current_role = DebaterRole.DEBATER_A
            self.current_turn += 1
    
    def add_message(
        self, 
        content: str, 
        audio_duration: Optional[float] = None,
        token_usage: Optional[TokenUsage] = None
    ) -> None:
        """Add a new message to the debate."""
        message = DebateMessage(
            role=self.current_role,
            content=content,
            turn_type=self.get_current_turn_type(),
            turn_number=self.current_turn,
            audio_duration=audio_duration,
            token_usage=token_usage
        )
        self.messages.append(message)
        
        # Update total token usage
        if token_usage:
            self.total_input_tokens += token_usage.input_tokens
            self.total_output_tokens += token_usage.output_tokens
            self.total_tokens += token_usage.total_tokens
        
        # Switch to next debater
        self.switch_debater()
        
        # Check if debate is complete (after switching debater)
        # Total messages should be max_turns * 2 (each debater gets max_turns)
        if len(self.messages) >= self.config.max_turns * 2:
            self.is_complete = True
            self.is_active = False
            
            # Log total token usage for completed debate
            from ..utils.logger import get_logger
            logger = get_logger()
            logger.info("Debate completed", 
                       topic=self.config.topic,
                       total_turns=len(self.messages),
                       total_input_tokens=self.total_input_tokens,
                       total_output_tokens=self.total_output_tokens,
                       total_tokens=self.total_tokens,
                       model=self.config.model)
    
    def get_messages_for_role(self, role: DebaterRole) -> List[DebateMessage]:
        """Get all messages from a specific debater."""
        return [msg for msg in self.messages if msg.role == role]
    
    def get_conversation_history(self) -> str:
        """Get formatted conversation history for AI context."""
        history = []
        for msg in self.messages:
            debater_name = "Debater A" if msg.role == DebaterRole.DEBATER_A else "Debater B"
            history.append(f"{debater_name}: {msg.content}")
        return "\n\n".join(history)