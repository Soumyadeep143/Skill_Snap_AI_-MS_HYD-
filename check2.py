import requests

GROQ_API_KEY = ""
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "model": "llama3-8b-8192",
    "messages": [{"role": "user", "content": "Hello! What can you do?"}],
    "temperature": 0.7
}

res = requests.post(url, headers=headers, json=data)
print(res.status_code)
print(res.text)
