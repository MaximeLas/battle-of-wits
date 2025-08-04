"""Prompt templates for AI debaters."""

from ..debate.models import DebaterRole, TurnType, DebateState


class PromptTemplates:
    """Templates for generating context-aware prompts for AI debaters."""
    
    SYSTEM_PROMPT_TEMPLATE = """You are an expert debater participating in a structured debate. Here are your key instructions:

DEBATE TOPIC: {topic}

YOUR POSITION: {your_position}
OPPONENT'S POSITION: {opponent_position}

DEBATE STRUCTURE:
- Total turns per debater: {max_turns}
- Current turn: {current_turn}
- Turn type: {turn_type}

ROLE AND BEHAVIOR:
- You are {debater_name} in this debate
- Defend your position with logical arguments, evidence, and persuasive rhetoric
- Address your opponent's points directly when they have been made
- Stay focused on the topic and maintain a respectful but assertive tone
- Be aware that this is turn {current_turn} of {max_turns} - pace your arguments accordingly

RESPONSE GUIDELINES:
- Keep responses between 100-300 words for opening/closing, 150-250 words for rebuttals
- Structure your argument clearly with main points
- Use evidence and reasoning to support your claims
- Acknowledge strong opposing points but counter them effectively
- Match the intensity and sophistication of your opponent

{turn_specific_instructions}

Remember: You are speaking aloud in a live debate. Make your response engaging and suitable for audio presentation."""

    TURN_INSTRUCTIONS = {
        TurnType.OPENING: """OPENING STATEMENT INSTRUCTIONS:
- Present your main thesis and 2-3 key supporting arguments
- Set the framework for how you'll approach this debate
- Be compelling and establish your credibility
- Do not yet respond to opponent arguments (they haven't spoken yet)""",
        
        TurnType.REBUTTAL: """REBUTTAL INSTRUCTIONS:
- This is a REBUTTAL - jump straight into addressing your opponent's arguments
- NO formal openings like "Ladies and gentlemen" - you're responding directly
- Point out specific flaws, contradictions, or weaknesses in their reasoning
- Present counter-evidence or alternative interpretations
- Strengthen your own position while dismantling theirs
- Reference specific points they made and explain why they're wrong
- Be conversational and direct - you're in the middle of an ongoing debate""",
        
        TurnType.CLOSING: """CLOSING ARGUMENT INSTRUCTIONS:
- Summarize your strongest points from the entire debate
- Highlight where you successfully countered your opponent
- Make a final compelling case for your position
- End with a memorable conclusion that reinforces your thesis
- This is your last chance to persuade - make it count"""
    }
    
    @classmethod
    def generate_system_prompt(cls, role: DebaterRole, state: DebateState) -> str:
        """Generate a context-aware system prompt for a debater."""
        config = state.config
        turn_type = state.get_current_turn_type()
        
        # Determine positions based on role
        if role == DebaterRole.DEBATER_A:
            your_position = config.position_a
            opponent_position = config.position_b
            debater_name = "Debater A"
        else:
            your_position = config.position_b
            opponent_position = config.position_a
            debater_name = "Debater B"
        
        turn_specific = cls.TURN_INSTRUCTIONS.get(turn_type, "")
        
        return cls.SYSTEM_PROMPT_TEMPLATE.format(
            topic=config.topic,
            your_position=your_position,
            opponent_position=opponent_position,
            max_turns=config.max_turns,
            current_turn=state.current_turn,
            turn_type=turn_type.value,
            debater_name=debater_name,
            turn_specific_instructions=turn_specific
        )
    
    @classmethod
    def generate_conversation_messages(cls, role: DebaterRole, state: DebateState) -> list:
        """Generate the conversation history formatted for OpenAI API."""
        messages = [
            {
                "role": "system",
                "content": cls.generate_system_prompt(role, state)
            }
        ]
        
        # Add conversation history
        if state.messages:
            # Add a user message to provide context about the debate history
            history = state.get_conversation_history()
            if history:
                messages.append({
                    "role": "user",
                    "content": f"Here is the debate so far:\n\n{history}\n\nNow it's your turn to respond."
                })
            else:
                messages.append({
                    "role": "user", 
                    "content": "Begin your opening statement."
                })
        else:
            messages.append({
                "role": "user",
                "content": "Begin your opening statement."
            })
        
        return messages