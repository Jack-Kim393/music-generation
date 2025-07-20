
import os
from gradio_client import Client
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
MUSICGEN_API_URL = os.getenv("MUSICGEN_API_URL")

def test_gradio_client():
    print(f"Testing Gradio Client with URL: {MUSICGEN_API_URL}")
    try:
        client = Client(src=MUSICGEN_API_URL, hf_token=HF_API_TOKEN)
        job = client.submit(
            text="A heroic and epic orchestral piece for a movie trailer",
            melody=None,
            duration=15,
            fn_index=0
        )
        print(f"Success! Result: {job.result()}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_gradio_client()
