"""Main debate controller that orchestrates the entire debate flow."""

import asyncio
from typing import Optional, AsyncGenerator, Tuple
from .models import DebateState, DebateConfig, DebaterRole
from .background_processor import BackgroundProcessor
from .presentation_manager import PresentationManager
from ..ai.debater import AIDebater
from ..audio.manager import AudioManager
from ..utils.logger import get_logger

logger = get_logger()


class DebateController:
    """Controls the entire debate flow and coordinates between AI and audio components."""
    
    def __init__(self):
        self.state: Optional[DebateState] = None
        self.debater_a: Optional[AIDebater] = None
        self.debater_b: Optional[AIDebater] = None
        self.audio_manager: Optional[AudioManager] = None
        self.background_processor: Optional[BackgroundProcessor] = None
        self.presentation_manager: Optional[PresentationManager] = None
        self._is_running = False
    
    def initialize_debate(self, config: DebateConfig) -> DebateState:
        """Initialize a new debate with the given configuration."""
        logger.info("Initializing debate with background processing", topic=config.topic)
        
        self.state = DebateState(config=config, is_active=True)
        
        # Initialize AI debaters
        self.debater_a = AIDebater(
            role=DebaterRole.DEBATER_A,
            position=config.position_a,
            opponent_position=config.position_b,
            config=config
        )
        
        self.debater_b = AIDebater(
            role=DebaterRole.DEBATER_B,
            position=config.position_b,
            opponent_position=config.position_a,
            config=config
        )
        
        # Initialize audio manager
        self.audio_manager = AudioManager(config)
        
        # Initialize background processing system
        self.background_processor = BackgroundProcessor(
            debate_state=self.state,
            debater_a=self.debater_a,
            debater_b=self.debater_b,
            audio_manager=self.audio_manager
        )
        
        self.presentation_manager = PresentationManager(
            debate_state=self.state,
            background_processor=self.background_processor
        )
        
        # Start background generation (always enabled for manual mode)
        self.background_processor.start_generation()
        logger.info("Background generation started")
        
        return self.state
    
    async def start_debate(self) -> AsyncGenerator[Tuple[str, bytes], None]:
        """
        Start the debate and yield (text, audio) pairs as they become available.
        This allows the UI to display text immediately while audio is being generated.
        """
        if not self.state or not self.debater_a or not self.debater_b or not self.audio_manager:
            raise ValueError("Debate not properly initialized")
        
        self._is_running = True
        
        while self.state.is_active and self._is_running:
            # Get current debater
            current_debater = (
                self.debater_a if self.state.current_role == DebaterRole.DEBATER_A 
                else self.debater_b
            )
            
            # Get voice for current debater
            voice = (
                self.state.config.tts_voice_a if self.state.current_role == DebaterRole.DEBATER_A
                else self.state.config.tts_voice_b
            )
            
            try:
                # Generate AI response
                response_text = await current_debater.generate_response(self.state)
                
                # Start audio generation in parallel
                audio_task = asyncio.create_task(
                    self.audio_manager.generate_audio(response_text, voice)
                )
                
                # Yield text immediately so UI can display it
                yield response_text, b''  # Empty bytes for now, audio comes next
                
                # Wait for audio to complete
                audio_data = await audio_task
                
                # Add message to state (this also switches debaters)
                self.state.add_message(response_text)
                
                # Yield the audio data
                yield '', audio_data  # Empty text, just audio
                
            except Exception as e:
                # Handle errors gracefully
                print(f"Error during debate turn: {e}")
                self.stop_debate()
                break
    
    def stop_debate(self) -> None:
        """Stop the current debate."""
        logger.info("Stopping debate and background processing")
        
        self._is_running = False
        if self.state:
            self.state.is_active = False
        
        # Stop background processing
        if self.background_processor:
            self.background_processor.stop_generation()
        
        if self.presentation_manager:
            self.presentation_manager.reset_presentation()
    
    def get_current_state(self) -> Optional[DebateState]:
        """Get the current debate state."""
        return self.state
    
    def is_running(self) -> bool:
        """Check if debate is currently running."""
        return self._is_running and self.state and self.state.is_active
    
    # New methods for background processing system
    
    def try_advance_presentation(self) -> Optional[bytes]:
        """Try to advance to the next turn. Returns audio data if advanced."""
        if not self.presentation_manager:
            return None
        
        advanced_turn = self.presentation_manager.advance_presentation()
        if advanced_turn:
            return advanced_turn.audio_data
        return None
    
    def get_current_audio(self) -> Optional[bytes]:
        """Get audio data for the current presentation."""
        if self.presentation_manager:
            return self.presentation_manager.get_current_audio()
        return None
    
    def has_ready_content(self) -> bool:
        """Check if there's content ready for presentation."""
        if self.presentation_manager:
            return self.presentation_manager.has_ready_content()
        return False
    
    def get_time_until_next_turn(self) -> Optional[float]:
        """Get seconds remaining until next turn."""
        if self.presentation_manager:
            return self.presentation_manager.get_time_until_next_turn()
        return None
    
    def pause_auto_advance(self) -> None:
        """Pause auto-advance presentation."""
        if self.presentation_manager:
            self.presentation_manager.pause_presentation()
    
    def resume_auto_advance(self) -> None:
        """Resume auto-advance presentation."""
        if self.presentation_manager:
            self.presentation_manager.resume_presentation()
    
    def get_buffer_ready_status(self) -> bool:
        """Check if background processor has ready turns."""
        if self.background_processor:
            return self.background_processor.has_ready_turns()
        return False
    
    def get_system_status(self) -> dict:
        """Get detailed status of the background processing system."""
        status = {
            "debate_active": self.state.is_active if self.state else False,
            "messages_count": len(self.state.messages) if self.state else 0,
            "background_processor": None,
            "presentation_manager": None
        }
        
        if self.background_processor:
            status["background_processor"] = self.background_processor.get_buffer_status()
        
        if self.presentation_manager:
            status["presentation_manager"] = self.presentation_manager.get_presentation_status()
        
        return status