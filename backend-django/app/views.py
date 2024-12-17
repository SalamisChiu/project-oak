from django.shortcuts import render
import random
import string
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .utils import firebase_auth_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from firebase_admin import auth as firebase_auth
import json
from django.conf import settings
from datetime import datetime
from .validators import PubSubMessageSchema
from google.cloud import pubsub_v1
from google.cloud import bigquery
from loguru import logger
bq_client = bigquery.Client()
PUBLISHER = pubsub_v1.PublisherClient()
TOPIC_PATH = PUBLISHER.topic_path(settings.GCP_PROJECT_ID, settings.PUBSUB_TOPIC_NAME)
BQ_TABLE = f"{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET_NAME}.{settings.BQ_TABLE_NAME}"
PROJECT_ID = settings.GCP_PROJECT_ID
DATASET_NAME = settings.BQ_DATASET_NAME
TABLE_NAME = settings.BQ_TABLE_NAME


@csrf_exempt
def verify_token(request):
    """
    驗證來自前端的 Firebase ID Token。
    """
    if request.method == "OPTIONS":
        # 處理預檢請求，返回允許的 HTTP 方法
        response = JsonResponse({"message": "Preflight OK"})
        response["Allow"] = "POST, OPTIONS"
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    if request.method == "POST":
        try:
            # 獲取前端發送的 JSON 數據
            data = json.loads(request.body)
            id_token = data.get("token")

            # 如果前端未提供 token，返回錯誤
            if not id_token:
                return JsonResponse({"error": "No token provided"}, status=400)

            # 驗證 ID Token
            decoded_token = firebase_auth.verify_id_token(id_token)
            user_id = decoded_token.get("uid")  # Firebase 用戶 ID

            # 可選：提取更多用戶信息（如 email 或 name）
            email = decoded_token.get("email", "No email provided")
            name = decoded_token.get("name", "No name provided")

            return JsonResponse(
                {
                    "message": "Token is valid",
                    "uid": user_id,
                    "email": email,
                    "name": name,
                },
                status=200,
            )

        except Exception as e:
            # 如果驗證失敗，返回錯誤信息
            return JsonResponse({"error": str(e)}, status=401)

    # 如果不是 POST 請求，返回錯誤
    return JsonResponse({"error": "Invalid request method"}, status=405)


def generate_short_code(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@csrf_exempt
@firebase_auth_required
def create_short_url(request):
    """
    創建短網址的視圖，僅允許 POST 請求，且需要 Firebase 驗證。
    """
    if request.method == "POST":
        try:
            # 驗證和解析請求數據
            data = json.loads(request.body)
            original_url = data.get("url")

            if not original_url:
                return JsonResponse({"error": "No URL provided"}, status=400)

            # 生成短碼並存入數據庫
            short_code = generate_short_code()

            # 創建消息數據
            message_data = {
                "short_code": short_code,
                "original_url": original_url,
                "timestamp": datetime.now().isoformat(),
                "action_type": "CREATE",
                "ip_address": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT"),
            }

            # 驗證消息數據結構
            validated_message = PubSubMessageSchema(**message_data)
            # 發送消息到 Pub/Sub
            future = PUBLISHER.publish(
                TOPIC_PATH, json.dumps(message_data).encode("utf-8")
            )
            future.result()  # 等待發送完成

            # 返回生成的短網址
            return JsonResponse(
                {"short_url": f"{settings.BASE_URL}/{short_code}"}, status=201
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except ValueError as e:
            return JsonResponse(
                {"error": "Invalid data", "details": str(e)}, status=400
            )

        except IntegrityError as e:
            return JsonResponse(
                {"error": "Database error", "details": str(e)}, status=500
            )

        except Exception as e:
            return JsonResponse(
                {"error": "Pub/Sub error", "details": str(e)}, status=500
            )

    return JsonResponse({"error": "Invalid request method"}, status=405)


def get_client_ip(request):
    logger.info("All META headers:")
    for key, value in request.META.items():
        logger.info(f"{key}: {value}")
    
    # 原有的 IP 獲取邏輯
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    
    #logger.info(f"Detected IP: {ip}")
    return ip


@csrf_exempt
def redirect_to_original(request, short_code):
    logger.info(f"Redirecting to original URL for short code: {short_code}")
    """
    重定向到原始 URL，並記錄點擊數據到 BigQuery。
    """
    # 從 BigQuery 查詢原始 URL
    query = f"""
    SELECT original_url 
    FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
    WHERE action_type = 'CREATE' 
    AND short_code = @short_code
    LIMIT 1
    """

    query_params = [bigquery.ScalarQueryParameter("short_code", "STRING", short_code)]
    job_config = bigquery.QueryJobConfig(query_parameters=query_params)

    try:
        query_job = bq_client.query(query, job_config=job_config)
        results = query_job.result()
        row = next(results)
        original_url = row.original_url

        # 構建點擊數據
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")
        if not ip_address:
            ip_address = "Unknown"
        if not user_agent:
            user_agent = "Unknown"
        message_data = {
            "short_code": short_code,
            "original_url": original_url,
            "timestamp": datetime.now().isoformat(),
            "action_type": "CLICK",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        # pubsub part
        validated_message = PubSubMessageSchema(**message_data)
        future = PUBLISHER.publish(TOPIC_PATH, json.dumps(message_data).encode("utf-8"))
        future.result()  # 等待發送完成

        # 返回重定向
        return redirect(original_url)

    except StopIteration:
        return JsonResponse({"error": "Short URL not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@firebase_auth_required
def click_statistics(request, short_code):
    """
    從 BigQuery 返回短碼的詳細統計數據，包括來源 IP 和點擊時間。
    """
    client = bigquery.Client(project=PROJECT_ID)

    # 查詢最近10筆點擊記錄
    recent_clicks_query = f"""
    SELECT 
        short_code,
        original_url,
        timestamp AS clicked_at,
        ip_address
    FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
    WHERE short_code = @short_code 
    AND action_type = 'CLICK'
    ORDER BY clicked_at DESC
    LIMIT 10
    """

    # 查詢總點擊次數
    click_count_query = f"""
    SELECT COUNT(*) as click_count
    FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
    WHERE short_code = @short_code 
    AND action_type = 'CLICK'
    """

    query_params = [bigquery.ScalarQueryParameter("short_code", "STRING", short_code)]
    job_config = bigquery.QueryJobConfig(query_parameters=query_params)

    try:
        # 執行最近點擊記錄查詢
        recent_clicks_job = client.query(recent_clicks_query, job_config=job_config)
        recent_clicks_rows = recent_clicks_job.result()

        # 執行點擊次數查詢
        click_count_job = client.query(click_count_query, job_config=job_config)
        click_count_row = next(click_count_job.result())

        # 格式化查詢結果
        clicks = []
        original_url = None
        for row in recent_clicks_rows:
            if not original_url:
                original_url = row.original_url
            clicks.append({
                "ip_address": row.ip_address,
                "clicked_at": row.clicked_at.isoformat() if row.clicked_at else None,
            })

        stats = {
            "short_code": short_code,
            "original_url": original_url,
            "click_count": click_count_row.click_count,
            "recent_clicks": clicks,  # 最近10筆點擊記錄
        }

        return JsonResponse(stats)

    except Exception as e:
        return JsonResponse(
            {"error": "Failed to fetch statistics", "details": str(e)}, status=500
        )


@csrf_exempt
def health_check(request):
    """
    Health Check API: 返回服務狀態和時間戳
    """
    return JsonResponse(
        {
            "status": "OK",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "message": "Backend is running successfully.",
        }
    )
