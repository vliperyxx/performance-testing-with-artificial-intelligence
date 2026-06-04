import os
from openai import OpenAI
import anthropic
from google import genai
from dotenv import load_dotenv

load_dotenv()

def call_openai(model, system_message, user_prompt, temperature=0):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as error:
        raise RuntimeError(f"OpenAI API error: {error}")

def call_anthropic(model, system_message, user_prompt, temperature=0, max_tokens=4096):
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
    except Exception as error:
        raise RuntimeError(f"Anthropic API error: {error}")

def call_gemini(model, system_message, user_prompt, temperature=0):
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        full_prompt = system_message + "\n\n" + user_prompt
        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
            config={"temperature": temperature}
        )
        return response.text
    except Exception as error:
        raise RuntimeError(f"Gemini API error: {error}")