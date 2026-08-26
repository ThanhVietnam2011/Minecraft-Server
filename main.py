import os
import json
from playwright.sync_api import sync_playwright

def renew_server():
    print("--- Bắt đầu tiến trình Renew Server ---")
    with sync_playwright() as p:
        # Chạy ở chế độ không giao diện
        browser = p.chromium.launch(headless=True)
        
        # Thiết lập cấu hình tránh bị phát hiện là Bot
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        # --- ĐOẠN NẠP COOKIE TỰ ĐỘNG ---
        # Lấy chuỗi Cookie cấu hình từ Environment Secret của GitHub để bảo mật
        cookie_env = os.environ.get("ZAMPTO_COOKIES")
        if cookie_env:
            try:
                cookies = json.loads(cookie_env)
                context.add_cookies(cookies)
                print("Đã nạp Cookie đăng nhập thành công.")
            except Exception as e:
                print(f"Lỗi cấu trúc Cookie: {e}")
        # -------------------------------

        page = context.new_page()
        
        try:
            # Truy cập thẳng vào trang server, giảm timeout xuống 30s để tránh bị treo vô hạn
            print("Đang truy cập dash.zampto.net...")
            page.goto("https://zampto.net", timeout=30000)
            
            # Đợi 5 giây cho trang ổn định
            page.wait_for_timeout(5000)

            # Tìm nút Renew chính xác bằng cả Text hoặc Selector cụ thể
            # Ép thời gian chờ nút xuất hiện tối đa là 15 giây
            renew_button = page.locator("button:has-text('Renew'), input[type='submit'][value*='Renew']").first
            
            if renew_button.is_visible(timeout=15000):
                renew_button.click()
                print("Đã click nút Renew Server thành công!")
                page.wait_for_timeout(3000) # Đợi 3 giây để request POST hoàn tất gửi đi
            else:
                print("Không tìm thấy nút Renew. Có thể Cookie đã hết hạn hoặc trang bị chặn bởi Cloudflare Captcha.")
                # Chụp ảnh màn hình lưu lại để bạn vào tab Artifacts xem lỗi nếu cần
                page.screenshot(path="error_screen.png")
                
        except Exception as e:
            print(f"Có lỗi xảy ra trong quá trình chạy: {e}")
        finally:
            browser.close()
            print("--- Kết thúc tiến trình ---")

if __name__ == "__main__":
    renew_server()
