# api_test.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

print("="*50)
print(f"Testing with Token: {HF_API_TOKEN}")
print("="*50)

def test_api_call():
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": "[INST] Say 'hello' in one word. [/INST]",
        "parameters": {"max_new_tokens": 10},
        "options": {"wait_for_model": True}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response

if __name__ == "__main__":
    print("API 호출을 시작합니다...")
    response = test_api_call()
    
    print("--- API 응답 결과 ---")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response JSON: {response.json()}")
    except requests.exceptions.JSONDecodeError:
        print(f"Response Text: {response.text}")
    print("--------------------")