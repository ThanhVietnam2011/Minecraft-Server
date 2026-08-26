import os
import json
import requests

def renew_server():
    print("--- Bắt đầu tiến trình API Renew Server ---")
    
    # 1. Lấy dữ liệu Cookie JSON từ GitHub Secret
    cookie_env = os.environ.get("ZAMPTO_COOKIES")
    if not cookie_env:
        print("Lỗi: Không tìm thấy ZAMPTO_COOKIES trong Secret!")
        return

    try:
        cookies_list = json.loads(cookie_env)
    except Exception as e:
        print(f"Lỗi phân tích JSON Cookie: {e}")
        return

    # Chuyển đổi định dạng Cookie phù hợp với thư viện requests
    session_cookies = {}
    csrf_token = ""
    for c in cookies_list:
        session_cookies[c["name"]] = c["value"]
        if c["name"] == "zampto_csrf":
            csrf_token = c["value"]

    # 2. Cấu hình Headers giả lập trình duyệt thật và nạp mã CSRF Token bắt buộc
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token, # Token bảo mật chống giả mạo request
        "Origin": "https://zampto.net",
        "Referer": "https://zampto.net/server?id=14221"
    }

    # 3. Dữ liệu Payload gửi đi (Gói ID server của bạn)
    # Dựa vào url cũ của bạn: id=14221
    payload = {
        "id": 14221
    }

    # 4. Tiến hành gửi request POST trực tiếp để Renew
    try:
        url = "https://zampto.net/api/server/renew"
        print(f"Đang gửi request POST tới {url}...")
        
        response = requests.post(url, headers=headers, cookies=session_cookies, json=payload, timeout=15)
        
        print(f"Mã phản hồi từ Server (Status Code): {response.status_code}")
        print(f"Nội dung phản hồi (Response): {response.text}")
        
        if response.status_code == 200 or "success" in response.text.lower():
            print("🎉 XÁC NHẬN: Đã tự động API Renew Server thành công!")
        else:
            print("Yêu cầu gửi đi thành công nhưng server từ chối gia hạn. Hãy kiểm tra lại Cookie.")

    except Exception as e:
        print(f"Lỗi kết nối khi gửi API: {e}")
    
    print("--- Kết thúc tiến trình ---")

if __name__ == "__main__":
    renew_server()
