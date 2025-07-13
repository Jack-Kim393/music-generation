import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 설정
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

print(f"MusicGen API URL: {os.getenv('MUSICGEN_API_URL')}")

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # 사용자가 양식을 '제출(POST)'했을 때의 로직
    if request.method == 'POST':
        user_prompt = request.form['prompt']
        print(f"사용자가 입력한 프롬프트: {user_prompt}")

        # --- 🤖 Gemini 호출 로직 시작 🤖 ---
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        lyricist_prompt = f"""
        [역할]: 당신은 최고의 K-pop 전문 작사가입니다.
        [목표]: 사용자가 입력한 '{user_prompt}'라는 주제에 맞춰, 10대와 20대가 공감할 트렌디한 노래 가사를 만들어주세요.
        [구조]: 1절, 후렴, 2절, 브릿지, 마지막 후렴 구조를 따라서 완성도 높은 가사를 만들어주세요.
        """
        response = model.generate_content(lyricist_prompt)
        lyrics = response.text

        print("--- 🎶 생성된 가사 🎶 ---")
        print(lyrics)
        print("--------------------")
        # --- Gemini 호출 로직 끝 ---

        # 1. HTML에서 줄바꿈을 위해, 생성된 가사의 '\n'을 '<br>'로 미리 바꾼다.
        formatted_lyrics = lyrics.replace('\n', '<br>')

        # 2. 미리 준비된 변수를 f-string 안에서 안전하게 사용한다.
        return f"요청: {user_prompt}<br><br>생성된 가사:<br>{formatted_lyrics}"

    # <<--- 이 부분이 추가되어야 합니다! ---<<
    # 사용자가 그냥 페이지를 '방문(GET)'했다면, 입력 페이지만 보여줍니다.
    return render_template('index.html')

# 이 파이썬 파일을 직접 실행했을 때만 아래 코드가 동작
if __name__ == '__main__':
    app.run(debug=True, port=5001)