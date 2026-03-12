import sys
import asyncio

import rich.console
import rich.traceback
import playwright.async_api
import playwright_stealth_plugin

console = rich.console.Console()
rich.traceback.install(console=console, show_locals=True)
sys.stderr = open("/dev/null", "w")

url = {
    "homepage": "https://chatgpt.com",
    "login": "https://chatgpt.com/auth/login_with",
    "email_login": "https://auth.openai.com/log-in",
    "password_login": "https://auth.openai.com/log-in/password",
    "push_auth": "https://auth.openai.com/push-auth-verification/*",
}

selector = {
    "email_input_field": "input[name='email']",
    "password_input_field": "input[name='current-password']",
    "submit_button": "button[type='submit']",
    "prompt_textarea": "div#prompt-textarea > p",
    "chat_button": "button[aria-label='Send prompt']",
    "voice_button": "button[aria-label='Start Voice']",
    "assistant_message": "[data-message-author-role='assistant']",
    "more_actions_button": "article[data-turn-id^='request-WEB']:last-of-type button[aria-label='More actions']",
    "read_aloud_button": "[data-radix-popper-content-wrapper] div[role='menuitem'][aria-label='Read aloud']",
}


async def account_check(page: playwright.async_api.Page) -> bool:
    await page.goto(url["homepage"], wait_until="networkidle", timeout=60000) if page.url != url["homepage"] else None
    return any(cookie.get("name") == "oai-gn" and cookie.get("value") == "Jaber" for cookie in await page.context.cookies())


async def login(email: str, password: str, page: playwright.async_api.Page):
    await page.goto(url["login"], wait_until="load")
    await page.wait_for_url(url["email_login"], wait_until="load")
    await page.fill(selector["email_input_field"], email)
    await page.locator(selector["submit_button"]).click()
    await page.wait_for_url(url["password_login"], wait_until="load")
    await page.fill(selector["password_input_field"], password)
    await page.locator(selector["submit_button"]).click()
    await page.wait_for_url(url["push_auth"], wait_until="load")
    async with page.expect_navigation(timeout=180000):
        console.print("Authorize on Your Phone ! Quick !")


async def chat(text: str, page: playwright.async_api.Page, timeout: float = 70000) -> str:
    await page.fill(selector["prompt_textarea"], text)
    await asyncio.sleep(min(len(text) * 0.05, 5))
    await page.click(selector["chat_button"])
    await page.wait_for_selector(selector["voice_button"], timeout=timeout)
    return (await page.locator(selector["assistant_message"]).nth(-1).inner_text()).strip() or "NO RESPONSE FOUND"


async def tts(text: str, page: playwright.async_api.Page, timeout: float = 70000) -> bytes:
    await chat(f"REPEAT TEXT: {text}", page, timeout=timeout)
    await page.click(selector["more_actions_button"])
    async with page.expect_response(lambda resp: "backend-api/synthesize" in resp.url and resp.status == 200, timeout=timeout) as resp_info:
        await page.click(selector["read_aloud_button"])
    response = await resp_info.value
    audio_bytes = await response.body()
    return audio_bytes


async def main():
    async with playwright.async_api.async_playwright() as pm:
        await playwright_stealth_plugin.async_apply(pm)
        context = await pm.chromium.launch_persistent_context("data", headless=True)
        page = await context.new_page()
        try:
            await page.goto(url["homepage"], wait_until="networkidle", timeout=60000)
            if not await account_check(page):
                console.print("Proceed to LOGIN !")
                email = console.input("[ EMAIL ] > ")
                password = console.input("[ PASSWORD ] > ")
                await login(email, password, page)
                assert await account_check(page), "LOGIN FAILURE !"
            console.print("Welcome to ChatGPT CLI !")
            await chat("Hello? Are you OK ?", page)
        except Exception as error:
            await page.screenshot(path="error_screenshot.png", full_page=True)
            console.print("SCREENSHOT: [cyan]error_screenshot.png[/cyan]")
            raise error
        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(main())
