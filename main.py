import os
import json
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def renew_server():
    print("--- Bắt đầu tiến trình Vượt Đố Cloudflare & Renew ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        
        page = context.new_page()
        stealth_sync(page) # Xóa nhận diện Bot
        
        # Nạp Cookie bảo mật từ GitHub Secret
        cookie_env = os.environ.get("ZAMPTO_COOKIES")
        if cookie_env:
            try:
                cookies = json.loads(cookie_env)
                valid_samesite = {"strict": "Strict", "lax": "Lax", "none": "None"}
                for cookie in cookies:
                    if "sameSite" in cookie:
                        ss_lower = str(cookie["sameSite"]).lower()
                        cookie["sameSite"] = valid_samesite.get(ss_lower, "Lax")
                context.add_cookies(cookies)
                print("-> Đã nạp Cookie thành công.")
            except Exception as e:
                print(f"Lỗi Cookie: {e}")
                return

        try:
            print("-> Đang tải trang quản lý server...")
            page.goto("https://zampto.net", timeout=60000)
            page.wait_for_timeout(5000)

            # --- KHU VỰC TỰ ĐỘNG CLICK Ô CAPTCHA CLOUDFLARE ---
            print("-> Kiểm tra lớp chặn Cloudflare Turnstile...")
            # Tìm tất cả các iframe chứa mã bảo vệ của Cloudflare Turnstile
            turnstile_frame = None
            for frame in page.frames:
                if "cloudflare" in frame.url or "turnstile" in frame.url:
                    turnstile_frame = frame
                    break
            
            if turnstile_frame:
                print("-> Phát hiện thấy ô xác thực Cloudflare! Đang tiến hành giải đố ngầm...")
                try:
                    # Tìm ô Checkbox bên trong iframe và click vật lý vào nó
                    checkbox = turnstile_frame.locator("#challenge-stage, .checkbox, input[type='checkbox']").first
                    if checkbox.is_visible():
                        checkbox.click()
                        print("-> Đã click vào ô xác thực Cloudflare. Đợi phản hồi hệ thống...")
                        page.wait_for_timeout(10000) # Đợi 10 giây để Cloudflare duyệt trạng thái
                except Exception as cf_err:
                    print(f"Không thể click ô bảo vệ: {cf_err}")
            else:
                print("-> Không thấy lớp chặn Turnstile hiển thị bề mặt, tiếp tục quét nút.")

            # --- TIẾN HÀNH RENEW SERVER ---
            renew_button = page.locator("button:has-text('Renew Server'), button:has-text('Renew')").first
            
            if renew_button.is_visible(timeout=10000):
                renew_button.click()
                print("🎉 XÁC NHẬN THÀNH CÔNG: Đã bẻ khóa bảo mật và CLICK RENEW thành công!")
                page.wait_for_timeout(5000)
            else:
                print("❌ THẤT BẠI: Vẫn không thấy nút Renew. Trang web đang bị khóa cứng giao diện.")
                page.screenshot(path="cloudflare_blocked.png")
                
        except Exception as e:
            print(f"❌ Lỗi thực thi: {e}")
        finally:
            browser.close()
            print("--- Kết thúc tiến trình ---")

if __name__ == "__main__":
    renew_server()
