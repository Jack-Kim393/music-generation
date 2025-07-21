# functions/main.py (최종 구문 오류 수정 버전)

from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore
import replicate
import os

initialize_app()

# -----------------------------------------------------------------
# 함수 1: 주문 접수 및 Replicate 작업 요청 (웨이터)
# -----------------------------------------------------------------
@https_fn.on_request(
    cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]),
    secrets=["REPLICATE_API_TOKEN"]
)
def generate_music(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST" or not req.is_json:
        return https_fn.Response("잘못된 요청입니다.", status=400)
    
    prompt = req.get_json().get("prompt")
    if not prompt:
        return https_fn.Response("프롬프트가 누락되었습니다.", status=400)

    db = firestore.client()
    doc_ref = db.collection("music_requests").document()
    doc_ref.set({
        "prompt": prompt,
        "status": "processing",
        "create_time": firestore.SERVER_TIMESTAMP
    })

    webhook_url = "https://webhook-yf6l5gdmia-uc.a.run.app" 

    try:
        prediction = replicate.predictions.create(
            version="riffusion/riffusion:8cf61ea6c56afd61d8f5b9ffd14d7c216c0a93844ce2d82ac1c9ecc9c7f24e05",
            input={"prompt_a": prompt},
            webhook=webhook_url,
            webhook_events_filter=["completed"]
        )
    except Exception as e:
        doc_ref.update({"status": "failed", "error": str(e)})
        return https_fn.Response(f"Replicate API 호출 오류: {str(e)}", status=500)

    doc_ref.update({"replicate_id": prediction.id})
    return https_fn.Response({"document_id": doc_ref.id}, mimetype="application/json")

# -----------------------------------------------------------------
# 함수 2: Replicate로부터 결과 수신 (주방장)
# -----------------------------------------------------------------
@https_fn.on_request(
    cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"])
)
def webhook(req: https_fn.Request) -> https_fn.Response:
    # ✅ 아래 라인의 누락된 부분을 제가 다시 채워넣었습니다!
    if req.method != "POST":
        return https_fn.Response("POST 요청만 허용됩니다.", status=405)

    result = req.get_json()
    replicate_