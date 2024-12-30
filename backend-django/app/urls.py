from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_short_url, name='create_short_url'),
    path("verify-token/", views.verify_token, name="verify_token"),  # 確保優先於動態路由
    path("health/", views.health_check, name="health_check"),  # 健康檢查路由
    path('<str:short_code>/stats/', views.click_statistics, name='click_statistics'),
    path('<str:short_code>', views.redirect_to_original, name='redirect_to_original'),
]
