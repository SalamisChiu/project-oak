from django.db import models

class ShortURL(models.Model):
    """
    短網址模型
    """
    original_url = models.URLField()  # 原始 URL
    short_code = models.CharField(max_length=10, unique=True)  # 短碼
    created_at = models.DateTimeField(auto_now_add=True)  # 創建時間
    click_count = models.IntegerField(default=0)  # 點擊次數

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"


class URLClick(models.Model):
    """
    點擊詳細記錄模型
    """
    short_url = models.ForeignKey(
        ShortURL, on_delete=models.CASCADE, related_name="clicks"
    )  # 關聯的短網址
    ip_address = models.GenericIPAddressField()  # 來源 IP
    clicked_at = models.DateTimeField(auto_now_add=True)  # 點擊時間

    def __str__(self):
        return f"Click on {self.short_url.short_code} from {self.ip_address}"