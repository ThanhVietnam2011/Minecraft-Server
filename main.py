import os
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def renew_server():
    print("--- Bắt đầu tiến trình Tự Động Đăng Nhập & Renew ---")
    
    # Lấy tài khoản mật khẩu bảo mật từ GitHub Secrets
    username = os.environ.get("ZAMPTO_EMAIL")
    password = os.environ.get("ZAMPTO_PASSWORD")
    
    if not username or not password:
        print("❌ LỖI: Chưa cấu hình ZAMPTO_EMAIL hoặc ZAMPTO_PASSWORD trong GitHub Secrets!")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        
        page = context.new_page()
        stealth_sync(page) # Xóa dấu vết nhận diện Bot

        try:
            # 1. Truy cập vào trang chủ hệ thống
            print("-> Đang tải trang chủ Zampto...")
            page.goto("https://zampto.net", timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(3000)

            # 2. Tìm và click nút Login trên thanh điều hướng để mở form đăng nhập
            print("-> Đang di chuyển tới trang Đăng nhập...")
            login_nav = page.locator("a:has-text('Login'), button:has-text('Login')").first
            if login_nav.is_visible():
                login_nav.click()
                page.wait_for_timeout(5000)
            else:
                # Nếu không thấy nút điều hướng, truy cập thẳng link dashboard đăng nhập
                page.goto("https://zampto.net", timeout=45000)
                page.wait_for_timeout(5000)

            # 3. Thực hiện điền dữ liệu vào Form đăng nhập
            print("-> Đang tự động nhập tài khoản và mật khẩu...")
            # Sử dụng bộ chọn tìm kiếm form linh hoạt theo thuộc tính loại input
            page.locator("input[type='email'], input[name='email'], input[placeholder*='Email']").first.fill(username)
            page.locator("input[type='password'], input[name='password'], input[placeholder*='Password']").first.fill(password)
            page.wait_for_timeout(1000)

            # Click nút Submit Đăng nhập
            submit_btn = page.locator("button[type='submit'], input[type='submit']").first
            submit_btn.click()
            print("-> Đã gửi thông tin Đăng nhập. Chờ xử lý hệ thống và Cloudflare...")
            page.wait_for_timeout(12000) # Đợi 12 giây để hệ thống chuyển hướng vào Dashboard chính

            # 4. Di chuyển thẳng đến trang quản lý Server sau khi đã đăng nhập thành công
            print("-> Đang truy cập thẳng vào trang quản lý Server ID 14221...")
            page.goto("https://zampto.net", timeout=45000)
            page.wait_for_timeout(7000)

            # 5. Tìm và click nút kích hoạt Renew Server
            renew_button = page.locator("button:has-text('Renew Server'), button:has-text('Renew')").first
            
            if renew_button.is_visible(timeout=10000):
                renew_button.click()
                print("🎉 XÁC NHẬN THÀNH CÔNG: Đã tự động đăng nhập và CLICK RENEW thành công!")
                page.wait_for_timeout(4000)
            else:
                print("❌ THẤT BẠI: Đăng nhập thành công nhưng không tìm thấy nút Renew. Vui lòng kiểm tra ảnh lỗi.")
                page.screenshot(path="cloudflare_blocked.png")
                
        except Exception as e:
            print(f"❌ Lỗi hệ thống: {e}")
            page.screenshot(path="cloudflare_blocked.png")
        finally:
            browser.close()
            print("--- Kết thúc tiến trình ---")

if __name__ == "__main__":
    renew_server()
