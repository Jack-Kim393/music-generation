# functions/main.py (Replicate API 최종 복원 버전)
import os
import json
import time
import requests
import traceback
from firebase_functions import https_fn
from firebase_functions.options import CorsOptions
from firebase_admin import initialize_app
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
initialize_app()

# .env 파일에서 Replicate API 토큰을 가져옵니다.
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# --- '소스' 레시피: 실제 Replicate API를 호출하는 부분 ---
def query_musicgen_api(prompt: str):
    """Replicate API를 사용하여 MusicGen을 호출하는 로직"""
    
    print(f"Replicate API에 '{prompt}' 작곡을 요청합니다...")
    
    try:
        start_response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "version": "b05b1dff1d8c6dc63d14b0cdb42135378dcb87f6373b0d3d341ede46e59e2b38",
                "input": { "prompt": prompt },
            },
        )
        
        prediction_data = start_response.json()
        prediction_id = prediction_data.get("id")
        
        if not prediction_id or start_response.status_code >= 400:
             print(f"Replicate 시작 요청 실패: {prediction_data.get('detail')}")
             return None

        print(f"생성 시작됨. ID: {prediction_id}. 결과를 기다립니다...")
        
        result_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
        while True:
            result_response = requests.get(
                result_url,
                headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"}
            )
            result_data = result_response.json()
            status = result_data.get("status")

            if status == "succeeded":
                print("음악 생성 성공!")
                return result_data.get("output")
            elif status == "failed":
                print(f"음악 생성 실패: {result_data.get('error')}")
                return None
            
            time.sleep(0.5)

    except Exception as e:
        print(f"--- Replicate API 호출 에러 ---\n{traceback.format_exc()}\n--- 에러 끝 ---")
        return None

# --- '메인 요리' 레시피: 사용자 요청을 받아 '소스' 레시피를 사용하는 부분 ---
# cors_origins에 우리 웹사이트의 공식 주소를 정확하게 적어줍니다.
@https_fn.on_request(
    cors=CorsOptions(
        cors_origins=["https://vibecoding-music-agent.web.app"], 
        cors_methods=["get", "post"]
    )
)
def generate_music(req: https_fn.Request) -> https_fn.Response:
    try:
        user_prompt = req.get_json(silent=True)['data']['prompt']
    except (TypeError, KeyError):
        return https_fn.Response('{"error": "..."}', status=400, mimetype="application/json")

    # '소스' 레시피를 호출합니다.
    music_url = query_musicgen_api(user_prompt)

    if music_url:
        response_data = json.dumps({"success": True, "music_url": music_url})
        return https_fn.Response(response_data, status=200, mimetype="application/json")
    else:
        response_data = json.dumps({"success": False, "error": "API 서버에서 음악 생성에 실패했습니다."})
        return https_fn.Response(response_data, status=500, mimetype="application/json")