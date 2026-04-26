"""Configuration management for API keys and environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Get Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY or GROQ_API_KEY == "gsk_placeholder_your_api_key_here":
    raise ValueError(
        """
        ❌ Groq API key not configured!
        
        Steps to fix:
        1. Get your FREE API key from: https://console.groq.com
        2. Copy the key from the console
        3. Open the .env file in this project directory
        4. Replace 'gsk_placeholder_your_api_key_here' with your actual key
        5. Save and restart the app
        
        Example .env file:
        GROQ_API_KEY=gsk_your_actual_key_here_1234567890
        """
    )

# Validate key format
if not GROQ_API_KEY.startswith("gsk_"):
    raise ValueError("Invalid Groq API key format. Should start with 'gsk_'")
