import os
import asyncio
from playwright.async_api import async_playwright

async def run():
    # Lấy thông tin tài khoản từ GitHub Secrets
    email = os.environ.get("ZAMPTO_EMAIL")
    password = os.environ.get("ZAMPTO_PASSWORD")
    server_id = os.environ.get("ZAMPTO_SERVER_ID")

    if not email or not password or not server_id:
        print("Lỗi: Chưa cấu hình đủ ZAMPTO_EMAIL, ZAMPTO_PASSWORD hoặc ZAMPTO_SERVER_ID trong GitHub Secrets!")
        return

    async with async_playwright() as p:
        # Cấu hình Chrome giả lập người dùng thật để vượt qua Cloudflare
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        try:
            # 1. Mở trang đăng nhập
            print("Đang truy cập trang đăng nhập...")
            await page.goto("https://dash.zampto.net/auth/login", wait_until="domcontentloaded")
            await page.wait_for_timeout(6000)  # Đợi Cloudflare verify ban đầu

            # 2. Điền thông tin đăng nhập
            print("Đang điền thông tin...")
            email_input = page.locator('input[type="email"], input[name="email"]').first
            password_input = page.locator('input[type="password"], input[name="password"]').first

            await email_input.fill(email)
            await password_input.fill(password)
            
            # Bấm nút Đăng nhập
            await page.locator('button[type="submit"]').click()
            await page.wait_for_timeout(6000)

            # 3. Chuyển sang trang Server
            server_url = f"https://dash.zampto.net/server?id={server_id}"
            print(f"Đang chuyển tới trang Server: {server_url}")
            await page.goto(server_url, wait_until="domcontentloaded")
            
            # Tạm dừng để Cloudflare Turnstile tự giải bài kiểm tra trên trang Server
            await page.wait_for_timeout(10000)

            # 4. Tìm và bấm nút Renew
            renew_button = page.get_by_role("button", name="Renew Server")
            if await renew_button.is_visible():
                await renew_button.click()
                print(" Thành công: Đã bấm Renew Server!")
                await page.wait_for_timeout(3000)
            else:
                print(" Không thấy nút 'Renew Server' (Có thể server đã được renew hoặc chưa tới giờ).")

        except Exception as e:
            print(f"Lỗi trong quá trình thực thi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
