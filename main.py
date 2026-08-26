import os
import json
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def renew_server():
    print("--- Bắt đầu tiến trình Bypass Cloudflare & Renew ---")
    with sync_playwright() as p:
        # Khởi chạy trình duyệt Chromium ẩn danh
        browser = p.chromium.launch(headless=True)
        
        # Cấu hình đầy đủ thông số giả lập thiết bị Windows thật 100%
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            locale="en-US",
            timezone_id="America/New_York"
        )
        
        page = context.new_page()
        
        # Kích hoạt chế độ tàng hình (Stealth) xóa sạch dấu vết Bot ẩn danh
        stealth_sync(page)
        
        # Nạp Cookie bảo mật từ GitHub Secret của bạn
        cookie_env = os.environ.get("ZAMPTO_COOKIES")
        if cookie_env:
            try:
                cookies = json.loads(cookie_env)
                # Đảm bảo định dạng chuẩn cho thuộc tính sameSite như đã xử lý trước đó
                valid_samesite = {"strict": "Strict", "lax": "Lax", "none": "None"}
                for cookie in cookies:
                    if "sameSite" in cookie:
                        ss_lower = str(cookie["sameSite"]).lower()
                        cookie["sameSite"] = valid_samesite.get(ss_lower, "Lax")
                context.add_cookies(cookies)
                print("-> Đã nạp và chuẩn hóa Cookie.")
            except Exception as e:
                print(f"Lỗi cấu trúc Cookie: {e}")
                return

        try:
            print("-> Đang tải trang quản lý server...")
            # Truy cập link và đợi trang tải ổn định trong tối đa 60 giây
            page.goto("https://zampto.net", timeout=60000, wait_until="networkidle")
            
            # Treo máy đợi thêm 15 giây để Cloudflare Turnstile ngầm tự động xác thực độ tin cậy
            print("-> Đang đợi Cloudflare kiểm tra dấu vân tay trình duyệt...")
            page.wait_for_timeout(15000)

            # Tìm nút Renew chính xác trên giao diện
            renew_button = page.locator("button:has-text('Renew Server'), button:has-text('Renew')").first
            
            # Kiểm tra xem nút có xuất hiện và sẵn sàng tương tác không
            if renew_button.is_visible(timeout=10000):
                # Thực hiện click vật lý giả lập người dùng thật di chuột đến
                renew_button.click()
                print("🎉 XÁC NHẬN: Hệ thống đã vượt Cloudflare thành công và CLICK RENEW!")
                page.wait_for_timeout(5000) # Đợi 5 giây để lưu lại trạng thái đổi mới
            else:
                print("❌ Không tìm thấy nút. Cloudflare Turnstile vẫn chặn đứng trang web.")
                # Chụp ảnh màn hình lưu lại để bạn kiểm tra nếu lỗi
                page.screenshot(path="cloudflare_blocked.png")
                
        except Exception as e:
            print(f"❌ Có lỗi xảy ra trong quá trình thực thi: {e}")
        finally:
            browser.close()
            print("--- Kết thúc tiến trình ---")

if __name__ == "__main__":
    renew_server()
