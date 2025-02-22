"""
Script to verify the Google Gemini API key configuration.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

def check_api_key_config():
    """Verify API key configuration and perform a test API call"""
    print("Verifying Google Gemini API key configuration...\n")

    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not found.")
        print("  Please ensure you have set the API key in the .env file in the project root.")
        return False

    if not api_key.startswith('AI') or len(api_key) < 20:
        print("❌ Error: API key format invalid.")
        print("  API keys should start with 'AI' and be at least 20 characters long.")
        print("  Please double-check your API key from Google AI Studio.")
        return False

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.0-pro")
        response = model.generate_content("Say 'test' to verify API key.")

        if response and response.text and "test" in response.text.lower():
            print("✅ API key verification successful!")
            print("   Successfully connected to Google Gemini API.")
            return True
        else:
            print("❌ Error: API test call failed.")
            print("   The API key may be valid, but the test call to Gemini failed.")
            print("   Response from API:", response)
            return False

    except Exception as e:
        print("❌ Error: API key verification failed due to an exception:")
        print(f"   {e}")
        if "API_KEY_INVALID" in str(e):
            print("\n   It seems the API key itself is invalid.")
            print("   Please generate a new API key from Google AI Studio and update your .env file.")
        elif "Quota" in str(e):
            print("\n   You may have exceeded your API quota or are being rate-limited.")
            print("   Check your Google AI Studio console for quota details.")
        else:
            print("\n   There might be a network issue or other configuration problem.")
            print("   Please check your internet connection and try again.")
        return False

def main():
    if check_api_key_config():
        print("\n🎉 Congratulations! Your Google Gemini API key is correctly configured.")
        print("   You can now run the dataset generator using:")
        print("   python src/main.py --total-conversations 1000")
    else:
        print("\n🛠️ API key verification failed. Please check the errors above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
