import requests
from app.config import Config


def generate_from_llm(prompt: str):
    if not Config.HF_MODEL_URL:
        raise Exception("HF_MODEL_URL is not configured")

    response = requests.post(
        Config.HF_MODEL_URL,
        headers={
            "Authorization": f"Bearer {Config.LLM_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 700,
                "temperature": 0.8,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True
            }
        }
    )

    if response.status_code != 200:
        raise Exception(f"LLM request failed: {response.status_code} {response.text}")

    return response.json()
