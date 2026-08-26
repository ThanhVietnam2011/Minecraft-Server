import os
import json
from playwright.sync_api import sync_playwright

def renew_server():
    print("--- Bắt đầu tiến trình Renew Server ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        # --- ĐOẠN NẠP COOKIE TỰ ĐỘNG (ĐÃ SỬA LỖI SAMESITE) ---
        cookie_env = os.environ.get("ZAMPTO_COOKIES")
        if cookie_env:
            try:
                cookies = json.loads(cookie_env)
                
                # Sửa lỗi định dạng sameSite để phù hợp với Playwright
                valid_samesite = {"strict": "Strict", "lax": "Lax", "none": "None"}
                for cookie in cookies:
                    if "sameSite" in cookie:
                        ss_lower = str(cookie["sameSite"]).lower()
                        if ss_lower in valid_samesite:
                            cookie["sameSite"] = valid_samesite[ss_lower]
                        else:
                            # Nếu giá trị không hợp lệ (như trống hoặc unspecfied), xóa hẳn thuộc tính này
                            del cookie["sameSite"]
                            
                context.add_cookies(cookies)
                print("Đã nạp và chuẩn hóa Cookie đăng nhập thành công.")
            except Exception as e:
                print(f"Lỗi cấu trúc Cookie: {e}")
        # ---------------------------------------------------

        page = context.new_page()
        
        try:
            print("Đang truy cập dash.zampto.net...")
            page.goto("https://zampto.net", timeout=30000)
            
            # Đợi 5 giây cho trang tải xong ổn định
            page.wait_for_timeout(5000)

            # Tìm nút Renew bằng text chính xác
            renew_button = page.locator("button:has-text('Renew Server'), button:has-text('Renew')").first
            
            if renew_button.is_visible():
                renew_button.click()
                print("Đã click nút Renew Server thành công!")
                page.wait_for_timeout(3000) # Đợi 3 giây để lệnh gửi đi hoàn tất
            else:
                print("Không tìm thấy nút Renew. Có thể Cookie đã hết hạn hoặc trang bị chặn bởi Cloudflare Captcha.")
                
        except Exception as e:
            print(f"Có lỗi xảy ra trong quá trình chạy: {e}")
        finally:
            browser.close()
            print("--- Kết thúc tiến trình ---")

if __name__ == "__main__":
    renew_server()
