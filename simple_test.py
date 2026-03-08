import requests

# Test OpenClaw connection
OPENCLAW_BASE_URL = "http://127.0.0.1:18789"
OPENCLAW_TOKEN = "556169250df6ecc690d82c22506b22aa0df844e0dbc64112"
OPENCLAW_CHAT_URL = f"{OPENCLAW_BASE_URL}/v1/chat/completions"

print("Testing OpenClaw connection...")

# Test health endpoint
try:
    response = requests.get(f"{OPENCLAW_BASE_URL}/health", timeout=5)
    print(f"Health endpoint: {response.status_code}")
except Exception as e:
    print(f"Health endpoint error: {e}")

# Test chat completions
try:
    headers = {"Content-Type": "application/json"}
    if OPENCLAW_TOKEN:
        headers["Authorization"] = f"Bearer {OPENCLAW_TOKEN}"
    
    payload = {
        "model": "openclaw:main",
        "messages": [{"role": "user", "content": "What is 2+2?"}],
    }
    
    response = requests.post(OPENCLAW_CHAT_URL, json=payload, headers=headers, timeout=10)
    print(f"Chat completions status: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Chat completions error: {e}")
