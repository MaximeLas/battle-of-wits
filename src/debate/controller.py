"""Main debate controller that orchestrates the entire debate flow."""

import asyncio
from typing import Optional, AsyncGenerator, Tuple
from .models import DebateState, DebateConfig, DebaterRole
from ..ai.debater import AIDebater
from ..audio.manager import AudioManager


class DebateController:
    """Controls the entire debate flow and coordinates between AI and audio components."""
    
    def __init__(self):
        self.state: Optional[DebateState] = None
        self.debater_a: Optional[AIDebater] = None
        self.debater_b: Optional[AIDebater] = None
        self.audio_manager: Optional[AudioManager] = None
        self._is_running = False
    
    def initialize_debate(self, config: DebateConfig) -> DebateState:
        """Initialize a new debate with the given configuration."""
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
        self._is_running = False
        if self.state:
            self.state.is_active = False
    
    def get_current_state(self) -> Optional[DebateState]:
        """Get the current debate state."""
        return self.state
    
    def is_running(self) -> bool:
        """Check if debate is currently running."""
        return self._is_running and self.state and self.state.is_active