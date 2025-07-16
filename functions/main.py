# functions/main.py
import os
import json
from firebase_functions import https_fn
from firebase_admin import initialize_app
from gradio_client import Client
from dotenv import load_dotenv

# 로컬 테스트를 위해 .env 파일 로드
load_dotenv()
# Firebase 앱 초기화
initialize_app()

# Hugging Face API 정보 (환경 변수에서 가져오기)
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
MUSICGEN_API_URL = os.getenv("MUSICGEN_API_URL")

def query_musicgen_api(prompt: str):
    """Gradio Client를 사용하여 MusicGen API를 호출하는 핵심 로직"""
    print(f"Gradio Client로 MusicGen에 '{prompt}' 작곡을 요청합니다...")
    try:
        client = Client(src=MUSICGEN_API_URL, hf_token=HF_API_TOKEN)
        # MusicGen 공식 Space API의 파라미터에 맞춰 predict 메소드 호출
        result = client.predict(
                        text=prompt,            # 텍스트 프롬프트
                        melody=None,            # 멜로디 입력 (사용 안 함)
                        duration=15,            # 생성할 오디오 길이 (초)
                        # gradio 버전에 따라 api_name 파라미터가 필요할 수 있음
                        # api_name="/predict" 
                )
        
        # result는 생성된 파일의 로컬 경로를 반환
        print(f"음악 생성 성공! 파일 경로: {result}")
        # 다운로드 가능한 전체 URL로 만들어 반환
        # gradio 4.x 버전부터는 파일 접근 URL 구조가 변경될 수 있습니다.
        # 아래는 일반적인 Hugging Face Space의 파일 URL 형식입니다.
        download_url = f"{MUSICGEN_API_URL}file={result}"
        return download_url
        
    except Exception as e:
        print(f"API 호출 중 에러 발생: {e}")
        return None

# 'generate_music'이라는 이름의 HTTP 호출 가능 함수
@https_fn.on_request(cors=https_fn.options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))
def generate_music(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP POST 요청을 받아 음악을 생성하고, 음악 파일 URL을 JSON으로 반환하는 API 엔드포인트.
    """
    # 요청 본문이 JSON이 아닐 경우를 대비한 예외 처리
    if not req.is_json:
        return https_fn.Response('{"error": "요청 형식이 JSON이 아닙니다."}', status=400, mimetype="application/json")
        
    try:
        # 예상 요청 형식: {"data": {"prompt": "신나는 우주여행 BGM"}}
        user_prompt = req.get_json(silent=True)['data']['prompt']
    except (TypeError, KeyError):
        return https_fn.Response('{"error": "요청 형식이 잘못되었습니다. {\'data\': {\'prompt\': \'주제\'}} 형식으로 보내주세요."}', status=400, mimetype="application/json")

    # 핵심 로직(작곡 함수) 호출
    music_url = query_musicgen_api(user_prompt)

    if music_url:
        # 성공 시, 생성된 음악 URL을 JSON 형태로 반환
        response_data = json.dumps({"success": True, "music_url": music_url})
        return https_fn.Response(response_data, status=200, mimetype="application/json")
    else:
        # 실패 시, 에러 메시지를 JSON 형태로 반환
        response_data = json.dumps({"success": False, "error": "API 서버에서 음악 생성에 실패했습니다."})
        return https_fn.Response(response_data, status=500, mimetype="application/json")