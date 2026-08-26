import os
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def renew_server():
    print("--- Bắt đầu tiến trình Đăng Nhập Hệ Thống & Renew ---")
    
    # Lấy tài khoản mật khẩu bảo mật từ GitHub Secrets
    username = os.environ.get("ZAMPTO_EMAIL")
    password = os.environ.get("ZAMPTO_PASSWORD")
    
    if not username or not password:
        print("❌ LỖI: Chưa cấu hình ZAMPTO_EMAIL hoặc ZAMPTO_PASSWORD trong GitHub Secrets!")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Bổ sung cấu hình ép bật JavaScript và giả lập phần cứng đồ họa máy thật
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True, # Ép buộc bật hoàn toàn JavaScript
            locale="en-US"
        )
        
        page = context.new_page()
        stealth_sync(page) # Tàng hình giấu cấu hình Bot đối với Cloudflare

        try:
            # 1. TRUY CẬP ĐƯỜNG DẪN ĐĂNG NHẬP CHUẨN XÁC
            print("-> Đang truy cập thẳng vào trang auth/login...")
            page.goto("https://dash.zampto.net/auth/login", timeout=60000, wait_until="networkidle")
            
            # Đợi 8 giây cho hệ thống nạp mã JavaScript và Cloudflare Turnstile tự duyệt
            print("-> Đang đợi tải Form và xử lý lớp bảo mật bảo vệ...")
            page.wait_for_timeout(8000)

            # 2. Xử lý click ô xác thực nếu Cloudflare Turnstile bị treo xoay tròn
            turnstile_frame = None
            for frame in page.frames:
                if "cloudflare" in frame.url or "turnstile" in frame.url:
                    turnstile_frame = frame
                    break
            
            if turnstile_frame:
                try:
                    checkbox = turnstile_frame.locator("#challenge-stage, .checkbox, input[type='checkbox']").first
                    if checkbox.is_visible():
                        checkbox.click()
                        print("-> Đã click hỗ trợ ô xác thực Cloudflare.")
                        page.wait_for_timeout(5000)
                except Exception:
                    pass

            # 3. TIẾN HÀNH ĐIỀN FORM ĐĂNG NHẬP (EMAIL / PASSWORD)
            print("-> Đang nhập tài khoản và mật khẩu vào Form...")
            
            # Định vị chính xác ô Email và Password trên trang auth/login
            email_field = page.locator("input[type='email'], input[name='email']").first
            password_field = page.locator("input[type='password'], input[name='password']").first
            
            # Đợi tối đa 15 giây cho đến khi ô nhập liệu xuất hiện (hết trạng thái Loading)
            email_field.wait_for(state="visible", timeout=15000)
            
            email_field.fill(username)
            password_field.fill(password)
            page.wait_for_timeout(1000)

            # Nhấn nút kích hoạt Đăng nhập hệ thống
            print("-> Nhấn nút Login...")
            submit_btn = page.locator("button:has-text('Login'), input[type='submit']").first
            submit_btn.click()
            
            print("-> Đang chờ hệ thống tạo phiên đăng nhập mới...")
            page.wait_for_timeout(12000) # Chờ 12 giây để hoàn thành chuyển hướng vào Dashboard chính

            # 4. Điều hướng thẳng tới trang cấu hình quản lý Server của bạn
            print("-> Điều hướng tới trang quản lý Server ID 14221...")
            page.goto("https://dash.zampto.net/server?id=14540", timeout=45000)
            page.wait_for_timeout(6000)

            # 5. Thực thi nhấn nút gia hạn Renew Server
            renew_button = page.locator("button:has-text('Renew Server'), button:has-text('Renew')").first
            
            if renew_button.is_visible(timeout=10000):
                renew_button.click()
                print("🎉 XÁC NHẬN THÀNH CÔNG: Hệ thống đã vượt qua mọi rào cản và CLICK RENEW thành công!")
                page.wait_for_timeout(4000)
            else:
                print("❌ THẤT BẠI: Đăng nhập thành công nhưng không tìm thấy nút Renew. Vui lòng kiểm tra ảnh lỗi.")
                page.screenshot(path="cloudflare_blocked.png")
                
        except Exception as e:
            print(f"❌ Lỗi hệ thống chi tiết: {e}")
            page.screenshot(path="cloudflare_blocked.png")
        finally:
            browser.close()
            print("--- Kết thúc tiến trình ---")

if __name__ == "__main__":
    renew_server()
