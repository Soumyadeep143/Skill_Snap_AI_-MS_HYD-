import requests
import json

GROQ_API_KEY = ""  # Replace with your Groq key
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "user", "content": "List 3 key responsibilities of a QA Engineer."}
    ],
    "temperature": 0.7
}

try:
    response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    data = response.json()
    print(" Groq API is working!")
    print(" Response:", data["choices"][0]["message"]["content"])
except requests.exceptions.RequestException as e:
    print(" Request failed:", e)
except Exception as ex:
    print(" Error parsing response:", ex)
