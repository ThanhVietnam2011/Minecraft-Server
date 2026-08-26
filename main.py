import os
import time
from playwright.sync_api import sync_playwright

def renew_server():
    print("--- Bắt đầu tiến trình Đăng Nhập Hệ Thống (Firefox Nhân Thực) & Renew ---")
    
    username = os.environ.get("ZAMPTO_EMAIL")
    password = os.environ.get("ZAMPTO_PASSWORD")
    
    if not username or not password:
        print("❌ LỖI: Chưa cấu hình ZAMPTO_EMAIL hoặc ZAMPTO_PASSWORD trong GitHub Secrets!")
        return

    with sync_playwright() as p:
        # Chuyển đổi sang nhân trình duyệt Firefox để bẻ gãy bộ quét Cloudflare Chrome-Bot
        browser = p.firefox.launch(headless=True)
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            locale="en-US"
        )
        
        page = context.new_page()

        try:
            # 1. TRUY CẬP TRANG ĐĂNG NHẬP
            print("-> Đang truy cập thẳng vào trang dash.zampto.net/auth/login...")
            page.goto("https://dash.zampto.net/auth/login", timeout=60000, wait_until="networkidle")
            
            # Đợi 10 giây để Firefox nạp đầy đủ mã vân tay dân dụng và Cloudflare tự kích hoạt thành công
            print("-> Đang đợi tải Form và xử lý lớp bảo mật bảo vệ...")
            page.wait_for_timeout(10000)

            # 2. ĐIỀN FORM ĐĂNG NHẬP
            print("-> Đang nhập tài khoản và mật khẩu vào Form...")
            email_field = page.locator("input[type='email'], input[name='email']").first
            password_field = page.locator("input[type='password'], input[name='password']").first
            
            email_field.wait_for(state="visible", timeout=15000)
            email_field.fill(username)
            password_field.fill(password)
            page.wait_for_timeout(1000)

            # Nhấn nút kích hoạt Đăng nhập
            print("-> Nhấn nút Login...")
            submit_btn = page.locator("button:has-text('Login'), input[type='submit']").first
            submit_btn.click()
            
            print("-> Đang chờ hệ thống tạo phiên đăng nhập mới...")
            page.wait_for_timeout(12000) 

            # 3. ĐIỀU HƯỚNG THẲNG ĐẾN TRANG QUẢN LÝ SERVER ĐÚNG ID 14540
            print("-> Điều hướng tới trang quản lý Server chính xác: dash.zampto.net/server?id=14540...")
            page.goto("https://dash.zampto.net/server?id=14540", timeout=45000)
            page.wait_for_timeout(8000)

            # 4. THỰC THI NHẤN NÚT RENEW SERVER
            print("-> Đang tìm nút Renew Server...")
            renew_button = page.locator("button:has-text('Renew Server'), button:has-text('Renew')").first
            
            if renew_button.is_visible(timeout=10000):
                renew_button.click()
                print("🎉 XÁC NHẬN THÀNH CÔNG: Hệ thống Firefox đã vượt qua mọi rào cản và CLICK RENEW THÀNH CÔNG!")
                page.wait_for_timeout(4000)
            else:
                print("❌ THẤT BẠI: Đang ở trang bảng điều khiển nhưng không thấy nút Renew. Vui lòng kiểm tra ảnh lỗi.")
                page.screenshot(path="cloudflare_blocked.png")
                
        except Exception as e:
            print(f"❌ Lỗi hệ thống chi tiết: {e}")
            page.screenshot(path="cloudflare_blocked.png")
        finally:
            browser.close()
            print("--- Kết thúc tiến trình ---")

if __name__ == "__main__":
    renew_server()
