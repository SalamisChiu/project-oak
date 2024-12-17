from django.http import JsonResponse
from firebase_admin import auth as firebase_auth

class FirebaseAuthenticationMiddleware:
    """
    中間件，用於全局驗證 Firebase ID Token
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 過濾不需要驗證的路由
        if request.path.startswith("/admin/") or request.path.startswith("/public/"):
            return self.get_response(request)

        # 獲取 Authorization 頭部
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=401)

        id_token = auth_header.split("Bearer ")[1]
        try:
            # 驗證 ID Token
            decoded_token = firebase_auth.verify_id_token(id_token)
            request.user = decoded_token  # 將解碼的 Token 信息存入 request
        except Exception as e:
            return JsonResponse({"error": "Invalid token"}, status=401)

        # 調用下一個中間件或視圖
        return self.get_response(request)