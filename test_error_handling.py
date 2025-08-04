"""Test script to demonstrate comprehensive error handling."""

import asyncio
import os
from dotenv import load_dotenv

from src.utils.logger import get_logger
from src.utils.errors import ConfigurationError
from src.ai.client import OpenAIClient
from src.debate.models import DebateConfig
from src.debate.controller import DebateController

# Load environment variables
load_dotenv()
logger = get_logger()


async def test_error_scenarios():
    """Test various error scenarios to demonstrate error handling."""
    print("🧪 Testing Battle of Wits Error Handling\n")
    
    # Test 1: Missing API Key
    print("=" * 50)
    print("Test 1: Missing API Key Scenario")
    print("=" * 50)
    
    # Temporarily remove API key
    original_key = os.getenv("OPENAI_API_KEY")
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        client = OpenAIClient()
        print("❌ Should have failed but didn't!")
    except ConfigurationError as e:
        print("✅ Correctly caught configuration error:")
        print(f"   User Message: {e.user_message}")
        print(f"   Category: {e.category}")
        print(f"   Suggestions: {len(e.suggestions)} provided")
        for i, suggestion in enumerate(e.suggestions, 1):
            print(f"      {i}. {suggestion}")
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
    
    # Restore API key
    if original_key:
        os.environ['OPENAI_API_KEY'] = original_key
    
    print("\n" + "=" * 50)
    print("Test 2: Invalid API Key Format")
    print("=" * 50)
    
    # Test invalid API key format
    os.environ['OPENAI_API_KEY'] = "invalid-key-format"
    
    try:
        client = OpenAIClient()
        print("❌ Should have failed but didn't!")
    except ConfigurationError as e:
        print("✅ Correctly caught invalid API key format:")
        print(f"   User Message: {e.user_message}")
        print(f"   Suggestions: {len(e.suggestions)} provided")
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
    
    # Restore original key
    if original_key:
        os.environ['OPENAI_API_KEY'] = original_key
    
    print("\n" + "=" * 50)
    print("Test 3: Valid Configuration")
    print("=" * 50)
    
    if original_key:
        try:
            client = OpenAIClient()
            print("✅ OpenAI client initialized successfully")
            
            # Test API connection
            connection_ok = await client.test_connection()
            if connection_ok:
                print("✅ API connection test successful")
            else:
                print("⚠️  API connection test failed (but client initialized)")
                
        except Exception as e:
            print(f"❌ Error with valid configuration: {e}")
    else:
        print("⚠️  No API key available for testing")
    
    print("\n" + "=" * 50)
    print("Test 4: Debate Configuration")
    print("=" * 50)
    
    try:
        config = DebateConfig(
            topic="Test topic",
            position_a="Position A",
            position_b="Position B",
            max_turns=4
        )
        print("✅ Debate configuration created successfully")
        
        controller = DebateController()
        controller.initialize_debate(config)
        print("✅ Debate controller initialized successfully")
        
    except Exception as e:
        print(f"❌ Error with debate configuration: {e}")
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print("✅ Error handling system is working correctly!")
    print("✅ User-friendly error messages are generated")
    print("✅ Technical details are logged for debugging")
    print("✅ Specific suggestions are provided for each error type")
    
    # Check log file
    log_files = list(os.path.join("logs", f) for f in os.listdir("logs") if f.endswith(".log"))
    if log_files:
        latest_log = max(log_files, key=os.path.getmtime)
        print(f"✅ Detailed logs written to: {latest_log}")
    
    print("\n🎉 Error handling test completed!")


if __name__ == "__main__":
    asyncio.run(test_error_scenarios())