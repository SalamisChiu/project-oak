FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 複製依賴並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製 Django 源碼
COPY . .

# 启动 Django 服务
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "backend.wsgi:application"]