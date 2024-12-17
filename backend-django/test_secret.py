# test_firebase_credentials.py
from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials
import os
import json

def test_firebase_credentials():
    try:
        # 初始化 Secret Manager 客戶端
        client = secretmanager.SecretManagerServiceClient()
        
        # 設定參數
        project_id = "fuller-oak1215"
        secret_id = "firebase-credentials"
        temp_path = "/tmp/firebase-test.json"
        
        # 獲取 secret
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        
        print("Successfully retrieved credentials from Secret Manager")
        
        # 將憑證寫入臨時文件
        with open(temp_path, "w") as f:
            f.write(secret_value)
        
        print(f"Credentials written to {temp_path}")
        
        # 測試 Firebase 初始化
        try:
            cred = credentials.Certificate(temp_path)
            firebase_admin.initialize_app(cred)
            print("Firebase successfully initialized!")
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
        
        # 清理臨時文件
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Temporary credential file removed from {temp_path}")
    
    except Exception as e:
        print(f"Error in process: {e}")

if __name__ == "__main__":
    test_firebase_credentials()