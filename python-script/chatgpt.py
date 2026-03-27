import sys
import asyncio

import rich.console
import rich.prompt
import rich.markdown
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
    "copy_response_button": "article:last-of-type button[aria-label='Copy response']",
    "more_actions_button": "article:last-of-type button[aria-label='More actions']",
    "read_aloud_button": "[data-radix-popper-content-wrapper] div[role='menuitem'][aria-label='Read aloud']",
}


async def account_check(page: playwright.async_api.Page) -> bool:
    if page.url != url["homepage"]:
        await page.goto(url["homepage"], wait_until="networkidle", timeout=60000)
    return any(cookie.get("name") == "oai-gn" and cookie.get("value") == "Jaber" for cookie in await page.context.cookies())


async def element_click(selector: str, page: playwright.async_api.Page):
    element = page.locator(selector)
    await element.wait_for(state="visible")
    await element.scroll_into_view_if_needed()
    bounding_box = await element.bounding_box()
    assert bounding_box, "Bounding Box isn't found !"
    await page.mouse.click(bounding_box["x"] + bounding_box["width"] / 2, bounding_box["y"] + bounding_box["height"] / 2)
    await asyncio.sleep(0.75)


async def login(email: str, password: str, page: playwright.async_api.Page):
    await page.goto(url["login"], wait_until="load")
    await page.wait_for_url(url["email_login"], wait_until="load")
    await page.fill(selector["email_input_field"], email)
    await page.locator(selector["submit_button"]).scroll_into_view_if_needed()
    await element_click(selector["submit_button"], page)
    await page.wait_for_url(url["password_login"], wait_until="load")
    await page.fill(selector["password_input_field"], password)
    await page.locator(selector["submit_button"]).scroll_into_view_if_needed()
    await element_click(selector["submit_button"], page)
    await page.wait_for_url(url["push_auth"], wait_until="load")
    async with page.expect_navigation(timeout=180000):
        console.print("Authorize on Your Phone ! Quick !")


async def chat(message_text: str, page: playwright.async_api.Page, timeout: float = 60000) -> str:
    await page.fill(selector["prompt_textarea"], message_text)
    await page.locator(selector["chat_button"]).scroll_into_view_if_needed()
    await element_click(selector["chat_button"], page)
    await page.wait_for_selector(selector["voice_button"], timeout=timeout)
    await page.locator(selector["copy_response_button"]).scroll_into_view_if_needed()
    await element_click(selector["copy_response_button"], page)
    return await page.evaluate("navigator.clipboard.readText()") or "NO RESPONSE FOUND"


async def tts(text: str, page: playwright.async_api.Page, timeout: float = 80000) -> bytes:
    await chat(f"REPEAT TEXT: {text}", page, timeout=timeout)
    await page.locator(selector["more_actions_button"]).scroll_into_view_if_needed()
    await element_click(selector["more_actions_button"], page)
    async with page.expect_response(lambda resp: "backend-api/synthesize" in resp.url and resp.status == 200, timeout=timeout) as resp_info:
        await page.locator(selector["read_aloud_button"]).scroll_into_view_if_needed()
        await element_click(selector["read_aloud_button"], page)
    return await (await resp_info.value).body()


async def main():
    async with playwright.async_api.async_playwright() as pcm:
        await playwright_stealth_plugin.async_apply(pcm)
        context = await pcm.chromium.launch_persistent_context("chatgpt-data", headless=False, permissions=["clipboard-read", "clipboard-write"])
        page = await context.new_page()
        try:
            await page.goto(url["homepage"], wait_until="networkidle", timeout=60000)
            if not await account_check(page):
                console.print("Proceed to LOGIN !")
                email = rich.prompt.Prompt.ask("[ EMAIL ] > ")
                password = rich.prompt.Prompt.ask("[ PASSWORD ] > ")
                await login(email, password, page)
                assert await account_check(page), "LOGIN FAILURE !"
            console.print("Welcome to ChatGPT CLI !")
            while True:
                console.rule("[USER]", characters="=", style="green")
                user_text = rich.prompt.Prompt.ask("[PROMPT] > ")
                if not user_text.startswith("/"):
                    console.print("INVALID ! Must start with '/' !")
                    continue
                match user_text.split(maxsplit=1):
                    case ["/chat", message]:
                        chatgpt_text = await chat(message, page)
                        console.rule("[CHATGPT]", characters="═", style="cyan")
                        console.print(rich.markdown.Markdown(chatgpt_text))
                    case ["/tts", message]:
                        chatgpt_audio = await tts(message, page)
                        console.rule("[CHATGPT]", characters="═", style="magenta")
                        with open(rich.prompt.Prompt.ask("[AUDIO_PATH] > "), "wb") as audio_file:
                            audio_file.write(chatgpt_audio)
                    case ["/exit"]:
                        console.print("AS YOU WISH ! MY LIFE MAY PERISH !")
                        break
                    case _:
                        console.print("INVALID ! Use /chat TEXT, /tts TEXT, /exit !")
        except Exception as error:
            await page.screenshot(path="error_screenshot.png", full_page=True)
            console.print("ERROR_SCREENSHOT: [cyan]error_screenshot.png[/cyan] !")
            raise error
        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(main())
