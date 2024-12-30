from django.http import JsonResponse
from firebase_admin import auth as firebase_auth
import functools

def firebase_auth_required(view_func):
    """
    裝飾器，用於驗證 Firebase ID Token
    """
    @functools.wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=401)

        id_token = auth_header.split("Bearer ")[1]
        try:
            # 驗證 ID Token
            decoded_token = firebase_auth.verify_id_token(id_token)
            request.user = decoded_token  # 將解碼的 Token 信息存入 request 對象
        except Exception as e:
            return JsonResponse({"error": "Invalid token"}, status=401)

        # 調用原始視圖
        return view_func(request, *args, **kwargs)

    return _wrapped_view