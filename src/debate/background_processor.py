"""Background processing system for debate generation."""

import asyncio
import threading
from queue import Queue, Empty
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import logging

from .models import DebateState, DebaterRole, DebateMessage, TokenUsage
from ..ai.debater import AIDebater
from ..audio.manager import AudioManager
from ..utils.logger import get_logger

logger = get_logger()


class GeneratedTurn:
    """Container for a fully generated turn (text + audio)."""
    
    def __init__(
        self, 
        role: DebaterRole,
        content: str,
        audio_data: bytes,
        token_usage: Optional[TokenUsage] = None,
        turn_number: int = 1,
        generated_at: Optional[datetime] = None
    ):
        self.role = role
        self.content = content
        self.audio_data = audio_data
        self.token_usage = token_usage
        self.turn_number = turn_number
        self.generated_at = generated_at or datetime.now()


class BackgroundProcessor:
    """Manages background generation of debate content."""
    
    def __init__(self, debate_state: DebateState, debater_a: AIDebater, debater_b: AIDebater, audio_manager: AudioManager):
        self.state = debate_state
        self.debater_a = debater_a
        self.debater_b = debater_b
        self.audio_manager = audio_manager
        
        # Queue system
        self.ready_queue: Queue[GeneratedTurn] = Queue()
        self.generation_active = False
        self.generation_thread: Optional[threading.Thread] = None
        
        # Buffer settings
        self.buffer_size = 3  # Stay 3 turns ahead
        self.generation_lock = threading.Lock()
        
        logger.info("Background processor initialized", buffer_size=self.buffer_size)
    
    def start_generation(self) -> None:
        """Start background generation thread."""
        if self.generation_active:
            logger.warning("Background generation already active")
            return
        
        self.generation_active = True
        self.generation_thread = threading.Thread(target=self._generation_worker, daemon=True)
        self.generation_thread.start()
        logger.info("Background generation started")
    
    def stop_generation(self) -> None:
        """Stop background generation thread."""
        self.generation_active = False
        if self.generation_thread and self.generation_thread.is_alive():
            self.generation_thread.join(timeout=5.0)
        logger.info("Background generation stopped")
    
    def _generation_worker(self) -> None:
        """Worker thread that generates content in background."""
        logger.info("Generation worker started")
        
        while self.generation_active and not self.state.is_complete:
            try:
                # Check if we need to generate more content
                current_turn = len(self.state.messages) + 1
                buffer_needed = current_turn + self.buffer_size
                generated_turns = self.ready_queue.qsize()
                
                if generated_turns < self.buffer_size:
                    # We need to generate more content
                    turn_to_generate = current_turn + generated_turns
                    max_total_turns = self.state.config.max_turns * 2  # Each debater gets max_turns
                    
                    if turn_to_generate <= max_total_turns and not self.state.is_complete:
                        self._generate_single_turn(turn_to_generate)
                    else:
                        # We've generated all possible turns or debate is complete
                        logger.info("Background generation stopping", 
                                   reason="max_turns_reached" if turn_to_generate > max_total_turns else "debate_complete")
                        break
                else:
                    # Buffer is full, wait a bit
                    threading.Event().wait(0.1)
                    
            except Exception as e:
                logger.error("Error in generation worker", error=e)
                threading.Event().wait(1.0)  # Wait before retrying
        
        logger.info("Generation worker finished")
    
    def _generate_single_turn(self, turn_number: int) -> None:
        """Generate a single turn (text + audio)."""
        try:
            # Determine which debater should speak
            role = DebaterRole.DEBATER_A if turn_number % 2 == 1 else DebaterRole.DEBATER_B
            current_debater = self.debater_a if role == DebaterRole.DEBATER_A else self.debater_b
            
            logger.info("Generating turn in background", turn=turn_number, debater=role.value)
            
            # Create temporary state for generation (snapshot current state)
            with self.generation_lock:
                temp_state = self._create_state_snapshot(turn_number, role)
            
            # Generate AI response (this is the slow part)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response_text, token_usage = loop.run_until_complete(
                    current_debater.generate_response(temp_state)
                )
                
                # Generate audio (also slow)
                voice = (
                    self.state.config.tts_voice_a if role == DebaterRole.DEBATER_A
                    else self.state.config.tts_voice_b
                )
                
                audio_data = loop.run_until_complete(
                    self.audio_manager.generate_audio(response_text, voice)
                )
                
                # Create generated turn
                generated_turn = GeneratedTurn(
                    role=role,
                    content=response_text,
                    audio_data=audio_data,
                    token_usage=token_usage,
                    turn_number=turn_number
                )
                
                # Add to ready queue
                self.ready_queue.put(generated_turn)
                
                logger.info("Turn generated successfully in background", 
                           turn=turn_number, 
                           debater=role.value,
                           queue_size=self.ready_queue.qsize(),
                           response_length=len(response_text),
                           audio_size=len(audio_data))
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error("Failed to generate turn in background", 
                        turn=turn_number, 
                        error=e)
    
    def _create_state_snapshot(self, turn_number: int, role: DebaterRole) -> DebateState:
        """Create a snapshot of the state for generation purposes."""
        # Create a copy of the current state for this specific turn
        snapshot = DebateState(
            config=self.state.config,
            messages=self.state.messages.copy(),  # Current messages so far
            current_turn=turn_number,
            current_role=role,
            is_active=True,
            is_complete=False
        )
        
        # Copy token tracking from original state
        snapshot.total_input_tokens = self.state.total_input_tokens
        snapshot.total_output_tokens = self.state.total_output_tokens  
        snapshot.total_tokens = self.state.total_tokens
        
        return snapshot
    
    def get_next_ready_turn(self) -> Optional[GeneratedTurn]:
        """Get the next ready turn from the queue (non-blocking)."""
        try:
            return self.ready_queue.get_nowait()
        except Empty:
            return None
    
    def has_ready_turns(self) -> bool:
        """Check if there are ready turns available."""
        return not self.ready_queue.empty()
    
    def get_buffer_status(self) -> Dict[str, Any]:
        """Get current buffer status for debugging."""
        return {
            "ready_turns": self.ready_queue.qsize(),
            "generation_active": self.generation_active,
            "buffer_size": self.buffer_size,
            "current_turn": len(self.state.messages) + 1
        }