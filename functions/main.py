# functions/main.py (비동기 1단계 버전)
import os, json, time, requests, traceback
from firebase_functions import https_fn
from firebase_functions.options import CorsOptions
from firebase_admin import initialize_app, firestore

load_dotenv()
initialize_app()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# (query_musicgen_api 함수는 다음 단계에서 사용할 것이므로 일단 그대로 둡니다)
# def query_musicgen_api(prompt: str):
#     ...

@https_fn.on_request(
    cors=CorsOptions(cors_origins=["https://vibecoding-music-agent.web.app"], cors_methods=["get", "post"])
)
def generate_music(req: https_fn.Request) -> https_fn.Response:
    """
    사용자의 요청을 받아 Firestore에 작업을 기록하고, 작업 ID를 즉시 반환하는 함수.
    """
    db = firestore.client() 

    try:
        user_prompt = req.get_json(silent=True)['data']['prompt']
    except (TypeError, KeyError):
        return https_fn.Response('{"error": "요청 형식이 잘못되었습니다."}', status=400, mimetype="application/json")

    try:
        # 1. 'predictions' 컬렉션에 새로운 문서를 만들어 '주문 번호표(ID)'를 생성합니다.
        doc_ref = db.collection("predictions").document()
        
        # 2. 주문서에 초기 내용을 기록합니다.
        print(f"Firestore에 작업 생성 중... ID: {doc_ref.id}")
        doc_ref.set({
            "prompt": user_prompt,
            "status": "processing", # 상태: 처리 중
            "createTime": firestore.SERVER_TIMESTAMP,
        })
        
        # 3. 사용자에게 '주문 번호표(ID)'를 전달하고 즉시 응답합니다.
        response_data = json.dumps({"success": True, "jobId": doc_ref.id})
        return https_fn.Response(response_data, status=202, mimetype="application/json") # 202: Accepted (요청이 접수됨)

    except Exception as e:
        print(f"Firestore 저장 실패: {e}")
        return https_fn.Response('{"error": "데이터베이스 요청 실패"}', status=500, mimetype="application/json")