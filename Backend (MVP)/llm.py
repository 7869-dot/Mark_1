import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure the Gemini API client
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_reply(message: str) -> str:
    """
    Calls the Gemini API to get a response to the user's message.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

async def generate_style_summary(writing_samples: list[str]) -> str:
    """
    Analyzes writing samples to generate a summary of the user's style.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = "Analyze these writing samples and summarize the writing style in a few sentences:\n\n"
        for i, sample in enumerate(writing_samples):
            prompt += f"Sample {i+1}: {sample}\n"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating style summary: {str(e)}"
