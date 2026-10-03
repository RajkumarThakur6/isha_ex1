import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Add it to your .env file.")

client = genai.Client(
    api_key=api_key,
    http_options=genai.types.HttpOptions(
        timeout=60000,
        retry_options=genai.types.HttpRetryOptions(attempts=1),
    ),
)


def ask_gemini(prompt):
    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt,
    )
    return response.output_text


if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    try:
        answer = ask_gemini(prompt)
        print(type(answer))
        print(answer)
    except Exception as error:
        print(f"Gemini request failed: {error}")
        print("Check your internet connection or try again later.")