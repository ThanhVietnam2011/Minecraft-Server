import time
import os
from playwright.sync_api import sync_playwright

def renew_server():
    print("--- Bắt đầu tiến trình Renew Server ---")
    with sync_playwright() as p:
        # Khởi chạy trình duyệt ẩn (Headless Chromium)
        browser = p.chromium.launch(headless=True)
        
        # Cấu hình User-Agent giả lập người dùng thật để tránh bị Cloudflare chặn
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        page = context.new_page()
        
        try:
            # 1. Truy cập vào trang quản lý Server của bạn
            # Thay đổi ID server (14221) nếu bạn đổi server mới
            page.goto("https://zampto.net", timeout=60000)
            
            # --- ĐOẠN NÀY DÀNH CHO ĐĂNG NHẬP (Nếu hệ thống bắt đăng nhập lại) ---
            # Nếu trang chuyển hướng về trang login, bạn cần code tự điền thông tin:
            # page.fill("input[type='email']", "tài_khoản_của_bạn")
            # page.fill("input[type='password']", "mật_khẩu_của_bạn")
            # page.click("button[type='submit']")
            # -----------------------------------------------------------------

            print("Đang đợi trang tải và Cloudflare Turnstile xác thực...")
            time.sleep(10) # Chờ 10 giây để Cloudflare xử lý token ngầm

            # 2. Tìm nút "Renew Server" dựa trên nội dung text hiển thị
            # Dựa vào ảnh của bạn, nút có chữ "Renew Server" màu trắng trên nền tím
            renew_button = page.locator("text=Renew Server")
            
            if renew_button.is_visible():
                renew_button.click()
                print("Đã click nút Renew Server thành công!")
                time.sleep(3) # Đợi 3 giây để lệnh POST gửi đi hoàn tất
            else:
                print("Không tìm thấy nút Renew Server (Có thể session đã hết hạn hoặc chưa đăng nhập).")
                
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
        finally:
            browser.close()
            print("--- Kết thúc tiến trình ---")

# Vòng lặp vô hạn chạy mỗi 5 phút (300 giây)
if __name__ == "__main__":
    while True:
        renew_server()
        print("Đợi 5 phút cho lần gia hạn tiếp theo...")
        time.sleep(300) 
