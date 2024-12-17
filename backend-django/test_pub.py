from google.cloud import pubsub_v1

# 設定你的 GCP 專案 ID 和 Pub/Sub 主題名稱
project_id = "fuller-oak1215"
topic_id = "oak-pubsub"

# 初始化 Publisher 客戶端
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# 要發佈的測試訊息
message_data = {
    "short_code": "abc123",
    "original_url": "https://www.example.com",
    "timestamp": "2024-12-16T16:00:00Z",
    "action_type": "CREATE",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# 發佈訊息到 Pub/Sub
def publish_message():
    try:
        # 將字典轉換為 JSON 字串
        import json
        message_json = json.dumps(message_data)
        
        # 將訊息轉換為 bytes
        message_bytes = message_json.encode("utf-8")
        
        # 發佈訊息
        future = publisher.publish(topic_path, message_bytes)
        print(f"Published message ID: {future.result()}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    publish_message()
