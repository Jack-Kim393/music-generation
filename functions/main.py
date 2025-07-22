# functions/main.py (JSON 응답 보강 최종 버전)

from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore
import replicate
import os
import json # ✅ JSON 라이브러리를 가져옵니다.

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
            input={
                "prompt_a": prompt,
                "duration": 15  # ✅ 15초 길이의 음악을 요청합니다! (원하는 숫자로 변경 가능)
            },
            webhook=webhook_url,
            webhook_events_filter=["completed"]
        )
    except Exception as e:
        doc_ref.update({"status": "failed", "error": str(e)})
        return https_fn.Response(f"Replicate API 호출 오류: {str(e)}", status=500)

    doc_ref.update({"replicate_id": prediction.id})
    
    # ✅ json.dumps를 사용해서 응답이 확실한 JSON 문자열임을 보장합니다.
    response_data = json.dumps({"document_id": doc_ref.id})
    return https_fn.Response(response_data, mimetype="application/json")

# -----------------------------------------------------------------
# 함수 2: Replicate로부터 결과 수신 (주방장)
# -----------------------------------------------------------------
@https_fn.on_request(
    cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"])
)
def webhook(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST":
        return https_fn.Response("POST 요청만 허용됩니다.", status=405)

    result = req.get_json()
    replicate_id = result.get("id")
    status = result.get("status")
    
    if not replicate_id or not status:
        return https_fn.Response("누락된 데이터가 있습니다.", status=400)

    db = firestore.client()
    query = db.collection("music_requests").where("replicate_id", "==", replicate_id).limit(1)
    docs = query.stream()
    doc_to_update = next(docs, None)
    
    if doc_to_update:
        update_data = {
            "status": "failed" if status != "succeeded" else "completed",
            "completed_time": firestore.SERVER_TIMESTAMP
        }
        if status == "succeeded":
            update_data["output_url"] = result.get("output", {}).get("audio")
        else:
            update_data["error"] = result.get("error", "Replicate에서 오류 발생")
        
        doc_to_update.reference.update(update_data)

    return https_fn.Response("웹훅 수신 완료", status=200)