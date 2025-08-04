"""Presentation manager for timed debate playback."""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import threading

from .models import DebateState
from .background_processor import BackgroundProcessor, GeneratedTurn
from ..utils.logger import get_logger

logger = get_logger()


class PresentationManager:
    """Manages the timed presentation of generated debate content."""
    
    def __init__(self, debate_state: DebateState, background_processor: BackgroundProcessor):
        self.state = debate_state
        self.processor = background_processor
        
        # Presentation state
        self.current_presentation: Optional[GeneratedTurn] = None
        self.presentation_start_time: Optional[datetime] = None
        self.presentation_lock = threading.Lock()
        
        logger.info("Presentation manager initialized")
    
    def has_ready_content(self) -> bool:
        """Check if there's content ready for presentation."""
        return self.processor.has_ready_turns()
    
    def advance_presentation(self) -> Optional[GeneratedTurn]:
        """Manually advance to the next turn if ready."""
        with self.presentation_lock:
            # Don't advance if debate is already complete
            if self.state.is_complete:
                logger.debug("Not advancing presentation - debate is complete")
                return None
            
            # Get next ready turn from background processor
            next_turn = self.processor.get_next_ready_turn()
            
            if next_turn:
                # Add to state (this updates the official debate state)
                self.state.add_message(
                    next_turn.content,
                    token_usage=next_turn.token_usage
                )
                
                # Update presentation tracking
                self.current_presentation = next_turn
                self.presentation_start_time = datetime.now()
                
                logger.info("Presentation advanced", 
                           turn=next_turn.turn_number,
                           debater=next_turn.role.value,
                           content_length=len(next_turn.content),
                           audio_size=len(next_turn.audio_data),
                           debate_complete=self.state.is_complete,
                           total_messages=len(self.state.messages))
                
                return next_turn
            else:
                logger.debug("No ready turns available for presentation")
                return None
    
    def get_current_audio(self) -> Optional[bytes]:
        """Get audio data for the current presentation."""
        with self.presentation_lock:
            if self.current_presentation:
                return self.current_presentation.audio_data
            return None
    
    def get_time_until_next_turn(self) -> Optional[float]:
        """Manual mode - no automatic timing. Always returns None."""
        return None
    
    def pause_presentation(self) -> None:
        """Manual mode - no pause/resume functionality needed."""
        logger.info("Manual mode - pause not applicable")
    
    def resume_presentation(self) -> None:
        """Manual mode - no pause/resume functionality needed."""
        logger.info("Manual mode - resume not applicable")
    
    def reset_presentation(self) -> None:
        """Reset presentation state (for new debates)."""
        with self.presentation_lock:
            self.current_presentation = None
            self.presentation_start_time = None
        logger.info("Presentation reset")
    
    def get_presentation_status(self) -> Dict[str, Any]:
        """Get current presentation status for debugging."""
        with self.presentation_lock:
            return {
                "has_current_presentation": self.current_presentation is not None,
                "manual_mode": True,
                "has_ready_content": self.has_ready_content(),
                "processor_buffer": self.processor.get_buffer_status()
            }