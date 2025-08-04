"""Simple test script to verify the setup works."""

import asyncio
import os
from dotenv import load_dotenv

from src.debate.models import DebateConfig
from src.debate.controller import DebateController

# Load environment variables
load_dotenv()


async def test_basic_setup():
    """Test basic setup and functionality."""
    print("🔧 Testing Battle of Wits setup...")
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        return False
    
    print("✅ OpenAI API key found")
    
    # Test debate configuration
    try:
        config = DebateConfig(
            topic="Is artificial intelligence beneficial for humanity?",
            position_a="AI will significantly benefit humanity",
            position_b="AI poses serious risks to humanity",
            max_turns=4  # Short test
        )
        print("✅ Debate configuration created successfully")
    except Exception as e:
        print(f"❌ Error creating debate config: {e}")
        return False
    
    # Test debate controller
    try:
        controller = DebateController()
        state = controller.initialize_debate(config)
        print("✅ Debate controller initialized successfully")
        print(f"📝 Topic: {state.config.topic}")
        print(f"🔵 Position A: {state.config.position_a}")
        print(f"🔴 Position B: {state.config.position_b}")
    except Exception as e:
        print(f"❌ Error initializing debate controller: {e}")
        return False
    
    print("\n🎉 Setup test completed successfully!")
    print("You can now run: streamlit run main.py")
    return True


if __name__ == "__main__":
    asyncio.run(test_basic_setup())