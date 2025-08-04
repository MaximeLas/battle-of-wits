"""Streamlit UI components for the debate application."""

import streamlit as st
from typing import Optional, List
from ..debate.models import DebateConfig, DebateState, DebateMessage


class DebateUI:
    """UI components for the debate application."""
    
    @staticmethod
    def render_setup_form() -> Optional[DebateConfig]:
        """Render the debate setup form and return configuration if submitted."""
        st.title("🥊 Battle of Wits")
        st.subheader("AI vs AI Debate Arena")
        
        with st.form("debate_setup"):
            # Topic input
            topic = st.text_input(
                "Debate Topic",
                placeholder="e.g., 'Artificial Intelligence will benefit humanity more than harm it'",
                help="Enter the topic or question that will be debated"
            )
            
            # Position inputs
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Debater A Position**")
                position_a = st.text_area(
                    "Position A",
                    placeholder="e.g., 'AI will significantly benefit humanity'",
                    help="The stance that Debater A will defend",
                    height=100,
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("**Debater B Position**")
                position_b = st.text_area(
                    "Position B", 
                    placeholder="e.g., 'AI poses serious risks to humanity'",
                    help="The stance that Debater B will defend",
                    height=100,
                    label_visibility="collapsed"
                )
            
            # Advanced settings in expandable section
            with st.expander("Advanced Settings"):
                col3, col4 = st.columns(2)
                
                with col3:
                    max_turns = st.select_slider(
                        "Turns per debater",
                        options=[4, 6, 8, 10, 12],
                        value=8,
                        help="Total number of turns each debater will get"
                    )
                    
                    model = st.selectbox(
                        "AI Model",
                        options=["gpt-4o", "gpt-4o-mini"],
                        index=0,
                        help="Choose the AI model for generating debate responses"
                    )
                
                with col4:
                    voice_a = st.selectbox(
                        "Voice for Debater A",
                        options=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        index=0
                    )
                    
                    voice_b = st.selectbox(
                        "Voice for Debater B", 
                        options=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        index=1
                    )
                    
                    tts_speed = st.slider(
                        "Speech Speed",
                        min_value=0.5,
                        max_value=2.0,
                        value=1.0,
                        step=0.1,
                        help="Speed of the generated speech"
                    )
            
            # Submit button
            submitted = st.form_submit_button(
                "🚀 Start Debate",
                type="primary",
                use_container_width=True
            )
            
            if submitted:
                # Validation
                if not topic.strip():
                    st.error("Please enter a debate topic")
                    return None
                
                if not position_a.strip():
                    st.error("Please enter Position A")
                    return None
                
                if not position_b.strip():
                    st.error("Please enter Position B")
                    return None
                
                # Create and return config
                return DebateConfig(
                    topic=topic.strip(),
                    position_a=position_a.strip(),
                    position_b=position_b.strip(),
                    max_turns=max_turns,
                    model=model,
                    tts_voice_a=voice_a,
                    tts_voice_b=voice_b,
                    tts_speed=tts_speed
                )
        
        return None
    
    @staticmethod
    def render_debate_header(state: DebateState) -> None:
        """Render the debate header with topic and progress."""
        st.title("🥊 Battle of Wits - Live Debate")
        
        # Topic display
        st.markdown(f"**Topic:** {state.config.topic}")
        
        # Positions
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🔵 Debater A:** {state.config.position_a}")
        with col2:
            st.markdown(f"**🔴 Debater B:** {state.config.position_b}")
        
        # Progress indicator
        progress = len(state.messages) / (state.config.max_turns * 2)
        st.progress(progress, text=f"Turn {state.current_turn} of {state.config.max_turns}")
        
        st.divider()
    
    @staticmethod
    def render_current_speaker(state: DebateState) -> None:
        """Render who is currently speaking."""
        if not state.is_active:
            return
        
        if state.is_complete:
            st.success("🎉 **Debate Complete!**")
            return
        
        current_debater = "Debater A 🔵" if state.current_role.value == "debater_a" else "Debater B 🔴"
        turn_type = state.get_current_turn_type().value.title()
        
        st.markdown(f"**Next Speaker:** {current_debater}")
        st.markdown(f"**Turn Type:** {turn_type}")
        
        # Show debate statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Messages", len(state.messages))
        with col2:
            st.metric("Current Turn", state.current_turn)
        with col3:
            st.metric("Remaining", state.config.max_turns - state.current_turn + 1)
    
    @staticmethod
    def render_transcript(messages: List[DebateMessage]) -> None:
        """Render the debate transcript."""
        st.subheader("📝 Debate Transcript")
        
        if not messages:
            st.info("Debate transcript will appear here as the debate progresses...")
            return
        
        for msg in messages:
            # Choose color and name based on role
            if msg.role.value == "debater_a":
                color = "blue"
                name = "Debater A"
                icon = "🔵"
            else:
                color = "red" 
                name = "Debater B"
                icon = "🔴"
            
            # Message container
            with st.container():
                st.markdown(f"**{icon} {name}** - {msg.turn_type.value.title()} (Turn {msg.turn_number})")
                st.markdown(f'<div style="border-left: 3px solid {color}; padding-left: 10px; margin-bottom: 20px;">{msg.content}</div>', 
                           unsafe_allow_html=True)
    
    @staticmethod
    def render_audio_player(audio_data: bytes, autoplay: bool = True) -> None:
        """Render audio player for TTS output."""
        if audio_data:
            st.audio(audio_data, format='audio/mp3', autoplay=autoplay)
    
    @staticmethod
    def render_debate_controls(state: DebateState) -> dict:
        """Render debate control buttons."""
        col1, col2, col3 = st.columns(3)
        
        controls = {}
        
        with col1:
            if state.is_active:
                controls['stop'] = st.button("⏹️ Stop Debate", type="secondary")
            else:
                controls['restart'] = st.button("🔄 New Debate", type="primary")
        
        with col2:
            if state.is_complete:
                controls['export'] = st.button("📤 Export Transcript")
        
        with col3:
            # Could add pause/resume functionality here in the future
            pass
        
        return controls
    
    @staticmethod
    def render_error_message(error) -> None:
        """Render comprehensive error message."""
        from ..utils.errors import BattleOfWitsError
        
        if isinstance(error, BattleOfWitsError):
            # Show user-friendly error with suggestions
            st.error(error.get_user_friendly_message())
            
            # Show technical details in expandable section for debugging
            with st.expander("🔧 Technical Details (for debugging)"):
                st.code(f"Category: {error.category}")
                st.code(f"Technical Message: {error.message}")
                if error.context:
                    st.json(error.context)
        else:
            # Fallback for other error types
            st.error(f"❌ An unexpected error occurred: {str(error)}")
    
    @staticmethod
    def render_system_status() -> None:
        """Render system status indicators."""
        st.sidebar.markdown("### 🔍 System Status")
        
        # This will be populated by the main app with real status checks
        if 'system_status' in st.session_state:
            status = st.session_state.system_status
            
            # API Connection Status
            if status.get('api_connected'):
                st.sidebar.success("✅ OpenAI API Connected")
            else:
                st.sidebar.error("❌ OpenAI API Disconnected")
            
            # Environment Status  
            if status.get('env_configured'):
                st.sidebar.success("✅ Environment Configured")
            else:
                st.sidebar.error("❌ Environment Issues")
                
            # Last updated
            if status.get('last_check'):
                st.sidebar.caption(f"Last checked: {status['last_check']}")
        else:
            st.sidebar.info("System status checking...")
    
    @staticmethod
    def render_completion_message(state: DebateState) -> None:
        """Render debate completion message."""
        if state.is_complete:
            st.success("🎉 Debate Complete!")
            st.balloons()
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Turns", len(state.messages))
            with col2:
                debater_a_msgs = len(state.get_messages_for_role(state.current_role))
                st.metric("Debater A Turns", debater_a_msgs)
            with col3:
                debater_b_msgs = len(state.messages) - debater_a_msgs
                st.metric("Debater B Turns", debater_b_msgs)