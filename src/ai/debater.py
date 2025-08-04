"""AI debater that generates contextual responses for debate turns."""

from typing import Optional, Tuple
from ..debate.models import DebaterRole, DebateState, DebateConfig, TokenUsage
from .client import get_openai_client
from .prompts import PromptTemplates


class AIDebater:
    """An AI debater that generates responses based on debate context and role."""
    
    def __init__(
        self, 
        role: DebaterRole, 
        position: str, 
        opponent_position: str, 
        config: DebateConfig
    ):
        self.role = role
        self.position = position
        self.opponent_position = opponent_position
        self.config = config
        self.client = get_openai_client()
    
    async def generate_response(self, state: DebateState) -> Tuple[str, TokenUsage]:
        """Generate a contextual response based on current debate state."""
        # Generate messages for this debater
        messages = PromptTemplates.generate_conversation_messages(self.role, state)
        
        try:
            # Call OpenAI API
            response = await self.client.create_chat_completion(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=500,  # Reasonable limit for debate responses
                stream=False  # We'll handle streaming at the UI level if needed
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")
            
            # Extract token usage
            usage = response.usage
            token_usage = TokenUsage(
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
                model=self.config.model
            )
            
            return content.strip(), token_usage
            
        except Exception as e:
            # Fallback response in case of API issues
            print(f"Error generating response for {self.role}: {e}")
            fallback_text = self._get_fallback_response(state)
            fallback_usage = TokenUsage(
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                model=self.config.model
            )
            return fallback_text, fallback_usage
    
    def _get_fallback_response(self, state: DebateState) -> str:
        """Generate a fallback response when API fails."""
        turn_type = state.get_current_turn_type()
        debater_name = "Debater A" if self.role == DebaterRole.DEBATER_A else "Debater B"
        
        fallback_responses = {
            "opening": f"I'm {debater_name}, and I strongly believe that {self.position}. "
                      f"Throughout this debate, I will demonstrate why this position is not only "
                      f"logical but necessary for our understanding of {state.config.topic}.",
            
            "rebuttal": f"While my opponent raises some points, I must respectfully disagree. "
                       f"The evidence clearly supports {self.position}, and I believe "
                       f"the arguments presented so far strengthen my position.",
            
            "closing": f"In conclusion, I have demonstrated that {self.position} is the most "
                      f"reasonable and well-supported position on {state.config.topic}. "
                      f"I believe the arguments presented today clearly favor my stance."
        }
        
        return fallback_responses.get(turn_type.value, fallback_responses["rebuttal"])