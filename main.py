"""Main Streamlit application for Battle of Wits."""

import streamlit as st
import asyncio
from typing import Optional
from datetime import datetime

from src.debate.controller import DebateController
from src.debate.models import DebateConfig, DebateState
from src.ui.components import DebateUI
from src.utils.logger import get_logger
from src.utils.errors import BattleOfWitsError, ConfigurationError
from src.ai.client import get_openai_client

# Initialize logger
logger = get_logger()


# Configure Streamlit page
st.set_page_config(
    page_title="Battle of Wits",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'debate_controller' not in st.session_state:
    st.session_state.debate_controller = DebateController()

if 'debate_active' not in st.session_state:
    st.session_state.debate_active = False

if 'current_audio' not in st.session_state:
    st.session_state.current_audio = None

if 'system_status' not in st.session_state:
    st.session_state.system_status = {}


def run_single_debate_turn():
    """Run a single turn of the debate synchronously."""
    controller = st.session_state.debate_controller
    
    if not controller.state or not controller.state.is_active or controller.state.is_complete:
        return
    
    try:
        # Get current debater
        from src.ai.debater import AIDebater
        from src.debate.models import DebaterRole
        
        current_debater = (
            controller.debater_a if controller.state.current_role == DebaterRole.DEBATER_A 
            else controller.debater_b
        )
        
        # Generate AI response synchronously using asyncio.run
        logger.info("Generating AI response", 
                   debater=controller.state.current_role.value,
                   turn=controller.state.current_turn)
        
        response_text = asyncio.run(current_debater.generate_response(controller.state))
        
        # Add message to state (this automatically switches to next debater)
        controller.state.add_message(response_text)
        
        logger.info("AI response generated successfully", 
                   debater=controller.state.current_role.value,
                   response_length=len(response_text))
        
        # Generate audio in background (simplified for now)
        voice = (
            controller.state.config.tts_voice_a if controller.state.current_role == DebaterRole.DEBATER_B
            else controller.state.config.tts_voice_b
        )
        
        try:
            audio_data = asyncio.run(controller.audio_manager.generate_audio(response_text, voice))
            st.session_state.current_audio = audio_data
        except Exception as audio_error:
            logger.error("Audio generation failed", error=audio_error)
            # Continue without audio
        
        return True
        
    except Exception as e:
        logger.error("Error during debate turn", error=e)
        DebateUI.render_error_message(e)
        controller.stop_debate()
        return False


async def check_system_status():
    """Check and update system status."""
    logger.info("Checking system status")
    
    status = {
        'last_check': datetime.now().strftime('%H:%M:%S'),
        'env_configured': False,
        'api_connected': False
    }
    
    try:
        # Test OpenAI client initialization and connection
        client = get_openai_client()
        status['env_configured'] = True
        
        # Test API connection (this might be slow, so we'll make it optional)
        status['api_connected'] = await client.test_connection()
        
    except Exception as e:
        logger.error("System status check failed", error=e)
        status['error'] = str(e)
    
    st.session_state.system_status = status
    return status


def main():
    """Main application function."""
    logger.info("Starting Battle of Wits application")
    
    # System status check
    DebateUI.render_system_status()
    
    # Check system status if not recently checked
    if not st.session_state.system_status.get('last_check'):
        with st.spinner("Checking system status..."):
            asyncio.run(check_system_status())
    
    controller = st.session_state.debate_controller
    
    # If no active debate, show setup form
    if not controller.state or not controller.state.is_active:
        config = DebateUI.render_setup_form()
        
        if config:
            # Initialize new debate
            try:
                logger.info("Initializing new debate", topic=config.topic)
                state = controller.initialize_debate(config)
                st.session_state.debate_active = True
                st.success("✅ Debate initialized! Starting now...")
                logger.info("Debate initialized successfully")
                st.rerun()
            except BattleOfWitsError as e:
                logger.error("Failed to initialize debate", error=e)
                DebateUI.render_error_message(e)
                return
            except Exception as e:
                logger.error("Unexpected error initializing debate", error=e)
                DebateUI.render_error_message(e)
                return
    
    else:
        # Active debate - show debate interface
        state = controller.state
        
        # Render debate header
        DebateUI.render_debate_header(state)
        
        # Create layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Main debate area
            DebateUI.render_current_speaker(state)
            
            # Auto-advance debate turns
            if state.is_active and not state.is_complete:
                # Auto-run first turn or show manual controls
                if len(state.messages) == 0:
                    # Automatically start the first turn
                    with st.spinner(f"AI is thinking... ({state.get_current_turn_type().value})"):
                        if run_single_debate_turn():
                            st.rerun()
                else:
                    # Manual turn advancement for subsequent turns
                    if st.button("▶️ Next Turn", key=f"turn_{len(state.messages)}"):
                        with st.spinner(f"AI is thinking... ({state.get_current_turn_type().value})"):
                            if run_single_debate_turn():
                                st.rerun()
            
            # Show completion message
            if state.is_complete:
                DebateUI.render_completion_message(state)
            
            # Debate controls
            controls = DebateUI.render_debate_controls(state)
            
            if controls.get('stop'):
                controller.stop_debate()
                st.session_state.debate_active = False
                st.rerun()
            
            if controls.get('restart'):
                # Reset for new debate
                st.session_state.debate_controller = DebateController()
                st.session_state.debate_active = False
                st.session_state.current_audio = None
                st.rerun()
        
        with col2:
            # Transcript
            DebateUI.render_transcript(state.messages)
            
            # Audio player for the most recent message
            if st.session_state.current_audio and len(state.messages) > 0:
                last_message = state.messages[-1]
                debater_name = "Debater A" if last_message.role.value == "debater_a" else "Debater B"
                st.subheader(f"🔊 {debater_name} Audio")
                DebateUI.render_audio_player(st.session_state.current_audio)


if __name__ == "__main__":
    main()