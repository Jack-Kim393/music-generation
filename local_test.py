
import requests
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="C:/Users/Jack/Desktop/vibecoding/music-generation/functions/.env")

url = "http://127.0.0.1:5001/vibecoding-music-agent/us-central1/generate_music"
data = {'data': {'prompt': 'A heroic and epic orchestral piece for a movie trailer'}}

try:
    response = requests.post(url, json=data)
    response.raise_for_status()  # Raise an exception for bad status codes
    print("Request successful!")
    print("Response:")
    print(response.text)
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
