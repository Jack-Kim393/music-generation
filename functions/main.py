# 필요한 라이브러리들을 가져옵니다.
from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore
import replicate
import os

# Firebase 앱을 초기화합니다.
initialize_app()
# 우리 웹사이트에서 오는 요청을 허용하도록 CORS 설정을 합니다.
options.set_global_options(cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]))

# 환경 변수에서 Replicate API 토큰을 가져와 설정합니다.
# (GCP Secret Manager에 REPLICATE_API_TOKEN 이름으로 비밀번호를 설정해두어야 합니다)
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

# -----------------------------------------------------------------
# 함수 1: 주문 접수 및 Replicate 작업 요청 (웨이터)
# -----------------------------------------------------------------
@https_fn.on_request(secrets=["REPLICATE_API_TOKEN"])
def generate_music(req: https_fn.Request) -> https_fn.Response:
    """사용자의 프롬프트 요청을 받아 Replicate에 작업을 전달하고, 즉시 응답하는 함수"""
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

    # ===================== 중요!! =====================
    # 이 URL은 아래 'webhook' 함수를 배포한 후에 얻을 수 있는 실제 URL로 교체해야 합니다.
    webhook_url = "여기에_배포된_webhook_함수_URL을_붙여넣으세요"
    # =================================================

    try:
        # Replicate에 음악 생성을 '시작'시키고, 결과 받을 주소(webhook)를 알려줍니다.
        prediction = replicate.predictions.create(
            version="riffusion/riffusion:8cf61ea6c56afd61d8f5b9ffd14d7c216c0a93844ce2d82ac1c9ecc9c7f24e05",
            input={"prompt_a": prompt},
            webhook=webhook_url,
            webhook_events_filter=["completed", "failed"] # 성공 또는 실패 시 알림 받기
        )
    except Exception as e:
        doc_ref.update({"status": "failed", "error": str(e)})
        return https_fn.Response(f"Replicate API 호출 오류: {str(e)}", status=500)

    doc_ref.update({"replicate_id": prediction.id})
    return https_fn.Response({"document_id": doc_ref.id}, mimetype="application/json")

# -----------------------------------------------------------------
# 함수 2: Replicate로부터 결과 수신 (주방장)
# -----------------------------------------------------------------
@https_fn.on_request()
def webhook(req: https_fn.Request) -> https_fn.Response:
    """Replicate에서 작업 완료 알림을 받는 함수"""
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