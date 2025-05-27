import os
import requests

USOM_URL = "https://www.usom.gov.tr/url-list.txt"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_PATH = os.path.join(BASE_DIR, "data", "url-list.txt")

def update_usom_list():
    print("USOM kara listesi indiriliyor...")
    try:
        os.makedirs(os.path.dirname(TARGET_PATH), exist_ok=True)
        response = requests.get(USOM_URL, timeout=30)
        if response.status_code == 200:
            with open(TARGET_PATH, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"✅ USOM kara listesi başarıyla güncellendi: {TARGET_PATH}")
        else:
            print(f"❌ Hata: USOM kara listesi indirilemedi! Kod: {response.status_code}")
    except Exception as e:
        print(f"❌ Beklenmeyen hata oluştu: {e}")

if __name__ == "__main__":
    update_usom_list()
