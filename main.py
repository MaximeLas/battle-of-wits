"""Main Streamlit application for Battle of Wits."""

import streamlit as st
import asyncio
import time
from datetime import datetime

from src.debate.controller import DebateController
from src.ui.components import DebateUI
from src.utils.logger import get_logger
from src.utils.errors import BattleOfWitsError
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

if 'auto_advance_timer' not in st.session_state:
    st.session_state.auto_advance_timer = None


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
    # Only log startup message once per session
    if 'app_started' not in st.session_state:
        logger.info("Starting Battle of Wits application")
        st.session_state.app_started = True

    # System status check
    DebateUI.render_system_status()

    # Check system status if not recently checked
    if not st.session_state.system_status.get('last_check'):
        with st.spinner("Checking system status..."):
            asyncio.run(check_system_status())

    controller = st.session_state.debate_controller

    # Show setup form only if no debate state or explicitly restarted
    # Completed debates should stay visible with completion UI
    if not controller.state or (not controller.state.is_active and not controller.state.is_complete):
        config = DebateUI.render_setup_form()

        if config:
            # Initialize new debate
            try:
                logger.info("Initializing new debate", topic=config.topic, auto_advance=config.auto_advance)
                state = controller.initialize_debate(config)

                # Initialize manual mode
                logger.info("Manual mode enabled - user controls advancement")

                st.session_state.debate_active = True
                st.success("✅ Debate initialized! Click 'Next Turn' to begin.")

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

        # Handle manual presentation advancement - no auto-advance needed

        # Create dynamic layout based on transcript content
        if len(state.messages) > 0:
            # More space for transcript when there's content
            col1, col2 = st.columns([1, 2])
        else:
            # More space for controls when transcript is empty
            col1, col2 = st.columns([2, 1])

        with col1:
            # Main debate area
            DebateUI.render_current_speaker(state)

            # Show status messages
            if state.is_active and not state.is_complete:
                if controller.has_ready_content():
                    st.success("✅ Next turn ready! Click 'Next Turn' to continue.")
                elif len(state.messages) == 0:
                    st.info("🚀 Debate starting - generating first response...")
                else:
                    st.info("⏳ Generating next response in background...")

            # Show completion message
            if state.is_complete:
                DebateUI.render_completion_message(state)

            # Debate controls (pass ready content status for better UX)
            has_ready = controller.has_ready_content() if controller else False
            controls = DebateUI.render_debate_controls(state, has_ready_content=has_ready)

        with col2:
            # Transcript
            DebateUI.render_transcript(state.messages)

            # Audio player for the current presentation
            current_audio = controller.get_current_audio()
            session_audio = st.session_state.get('current_audio')

            # Audio availability check

            if current_audio and len(state.messages) > 0:
                last_message = state.messages[-1]
                debater_name = "Debater A" if last_message.role.value == "debater_a" else "Debater B"
                st.subheader(f"🔊 {debater_name} Audio")
                DebateUI.render_audio_player(current_audio)
            elif session_audio and len(state.messages) > 0:
                # Fallback to session audio if available
                last_message = state.messages[-1]
                debater_name = "Debater A" if last_message.role.value == "debater_a" else "Debater B"
                st.subheader(f"🔊 {debater_name} Audio (Session)")
                DebateUI.render_audio_player(session_audio)
            else:
                st.info("🔇 No audio available yet")

        # Handle control actions AFTER both columns are rendered
        if controls.get('next_turn'):
            # Manual advance to next turn
            if controller.has_ready_content():
                audio_data = controller.try_advance_presentation()
                if audio_data:
                    st.session_state.current_audio = audio_data
                    logger.info("Manual presentation advanced",
                               audio_size=len(audio_data),
                               total_messages=len(state.messages),
                               debate_complete=state.is_complete)
                    st.rerun()
                else:
                    st.error("❌ Error advancing presentation - please try again")
                    st.rerun()
            else:
                st.warning("⏳ Next turn is still being generated, please wait...")
                time.sleep(1.0)  # Give more time for generation
                st.rerun()

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

        # Auto-start first turn if no messages yet
        if state.is_active and not state.is_complete and len(state.messages) == 0:
            has_content = controller.has_ready_content()
            
            if has_content:
                audio_data = controller.try_advance_presentation()
                if audio_data:
                    st.session_state.current_audio = audio_data
                    logger.info("Auto-started first turn",
                               audio_size=len(audio_data),
                               total_messages=len(state.messages))
                    st.rerun()
                else:
                    logger.warning("has_ready_content was True but try_advance_presentation returned None")
            else:
                # Trigger a rerun to check again soon
                time.sleep(0.5)
                st.rerun()


if __name__ == "__main__":
    main()