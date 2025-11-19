import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables.")
    sys.exit(1)

# Initialize Gemini client
client = genai.Client(api_key=api_key)

def main():
    # CLI argument parsing
    parser = argparse.ArgumentParser(description="Gemini CLI prompt tool")
    parser.add_argument("prompt", type=str, help="Prompt to send to the model")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    user_prompt = args.prompt
    verbose = args.verbose

    # Create messages list for Gemini
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    # Generate response
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages
    )

    # Verbose output
    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    # Always print the model response
    print(response.text)

if __name__ == "__main__":
    main()

