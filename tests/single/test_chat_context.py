
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parents[2]))

# Mock google.genai specifically, preserving other google packages (like protobuf)
mock_genai = MagicMock()
sys.modules['google.genai'] = mock_genai

# Ensure from google import genai works
try:
    import google
    google.genai = mock_genai
except ImportError:
    # If google package doesn't exist at all, we can mock it, but yfinance needs it.
    # We assume yfinance's dependencies are present, so google should exist.
    pass

from app.main import app

client = TestClient(app)

def test_chat_context_injection():
    """
    Verify that the 'context' field in the request body is correctly
    injected into the system prompt passed to the AI model.
    """
    payload = {
        "message": "Should I sell TSMC?",
        "context": "TSMC (2330): CAGR 22.2%, Volatility 15%",
        "apiKey": "fake-key",
        "isPremium": True
    }

    # Mock the genai Client and its method
    with patch("app.main.genai.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.models.generate_content.return_value.text = "Mock Response"

        response = client.post("/api/chat", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"response": "Mock Response"}
        
        # Verify the call arguments
        # We expect the context to be in the system prompt (first message)
        args, kwargs = mock_instance.models.generate_content.call_args
        contents = kwargs['contents']
        
        system_msg = contents[0]['parts'][0]['text']
        
        # Check if context was injected
        assert "USER PORTFOLIO CONTEXT:" in system_msg
        assert "TSMC (2330): CAGR 22.2%, Volatility 15%" in system_msg
        
        # Check if MoneyCome logic instructions are present (from updated PROMPT_PREMIUM)
        assert "MoneyCome" in system_msg
        assert "CAGR Truth" in system_msg

if __name__ == "__main__":
    # Manually run the test if executed directly
    try:
        test_chat_context_injection()
        print("Test Passed: Context correctly injected into Prompt!")
    except AssertionError as e:
        print(f"Test Failed: {e}")
    except Exception as e:
        print(f"Test Error: {e}")
