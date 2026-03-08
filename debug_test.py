import requests
import json

# Test OpenClaw connection with debugging
OPENCLAW_BASE_URL = "http://127.0.0.1:18789"
OPENCLAW_TOKEN = "556169250df6ecc690d82c22506b22aa0df844e0dbc64112"
OPENCLAW_CHAT_URL = f"{OPENCLAW_BASE_URL}/v1/chat/completions"

print("=== OpenClaw Debug Test ===")
print(f"Base URL: {OPENCLAW_BASE_URL}")
print(f"Chat URL: {OPENCLAW_CHAT_URL}")
print(f"Token: {OPENCLAW_TOKEN}")
print()

# Test 1: Health check
print("1. Testing health endpoint...")
try:
    response = requests.get(f"{OPENCLAW_BASE_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 2: Chat completions
print("2. Testing chat completions...")
try:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENCLAW_TOKEN}"
    }
    
    payload = {
        "model": "xai/grok-beta",
        "messages": [{"role": "user", "content": "What is 2+2?"}],
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print(f"   Headers: {headers}")
    
    response = requests.post(OPENCLAW_CHAT_URL, json=payload, headers=headers, timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if "choices" in data and data["choices"]:
            content = data["choices"][0]["message"]["content"]
            print(f"   AI Response: {content}")
    
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Check available models
print("3. Testing models endpoint...")
try:
    response = requests.get(f"{OPENCLAW_BASE_URL}/v1/models", headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print(f"   Available models: {json.dumps(models, indent=2)}")
except Exception as e:
    print(f"   Error: {e}")
