# app.py (MusicGen 최종 버전)
import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
load_dotenv()

MUSICGEN_API_URL = os.getenv("MUSICGEN_API_URL")
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

app = Flask(__name__)
print("DEBUG: After Flask app initialization")

# MusicGen API를 호출하는 함수 (fn_index 최종 버전)
def query_musicgen_api(prompt):
    from gradio_client import Client
    print(f"Gradio Client로 MusicGen에 '{prompt}' 작곡을 요청합니다...")
    try:
        # 인증 토큰을 포함하여 클라이언트 생성
        # client = Client(MUSICGEN_API_URL, hf_token=HF_API_TOKEN)
        # 클라이언트를 함수 내에서 생성하여 앱 시작 시 지연 방지
        client = Client(MUSICGEN_API_URL, hf_token=HF_API_TOKEN)
        
        # '이름' 대신 '순서(fn_index)'로 API를 호출합니다.
        result = client.predict(
                        prompt, # 0번째 파라미터: Describe your music
                        fn_index=0
                )
        
        print(f"음악 생성 성공! 파일 경로: {result}")
        # 다운로드 가능한 전체 URL로 만들어 반환
        download_url = f"{MUSICGEN_API_URL}file={result}"
        return download_url

    except Exception as e:
        print(f"API 호출 중 에러 발생: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    music_url = None
    user_prompt = ""
    if request.method == 'POST':
        user_prompt = request.form['prompt']
        print(f"사용자가 입력한 음악 프롬프트: {user_prompt}")
        music_url = query_musicgen_api(user_prompt)

    return render_template('index.html', music_url=music_url, prompt=user_prompt)

if __name__ == '__main__':
    print("DEBUG: Before app.run()")
    app.run(debug=True, port=5001)