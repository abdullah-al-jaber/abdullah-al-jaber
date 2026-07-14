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
    "copy_response_button": "section[data-turn='assistant']:last-of-type button[aria-label='Copy response']",
    "more_actions_button": "section[data-turn='assistant']:last-of-type button[aria-label='More actions']",
    "read_aloud_button": "[data-radix-popper-content-wrapper] div[role='menuitem'][aria-label='Read aloud']",
}


async def account_check(page: playwright.async_api.Page) -> bool:
    assert page.url != url["homepage"], "Account Check Homepage Mismatch !"
    return any(cookie.get("name") == "oai-gn" and cookie.get("value") == "Jaber" for cookie in await page.context.cookies())


async def element_click(selector: str, page: playwright.async_api.Page, delay: float = 1.25):
    element = page.locator(selector)
    await element.wait_for(state="visible")
    await element.scroll_into_view_if_needed()
    bounding_box = await element.bounding_box()
    assert bounding_box, "Bounding Box isn't found !"
    await page.mouse.click(bounding_box["x"] + bounding_box["width"] / 2, bounding_box["y"] + bounding_box["height"] / 2)
    await asyncio.sleep(delay)


async def login(email: str, password: str, page: playwright.async_api.Page, authorize_timeout: float = 300_000):
    await page.goto(url["login"], wait_until="load")
    await page.wait_for_url(url["email_login"], wait_until="load")
    await page.fill(selector["email_input_field"], email)
    await element_click(selector["submit_button"], page)
    await page.wait_for_url(url["password_login"], wait_until="load")
    await page.fill(selector["password_input_field"], password)
    await element_click(selector["submit_button"], page)
    await page.wait_for_url(url["push_auth"], wait_until="load")
    async with page.expect_navigation(timeout=authorize_timeout):
        console.print("Authorize on Your Phone ! Quick !")


async def chat(text: str, page: playwright.async_api.Page, response_timeout: float = 150_000) -> str:
    await page.fill(selector["prompt_textarea"], text)
    await element_click(selector["chat_button"], page)
    await page.wait_for_selector(selector["voice_button"], timeout=response_timeout)
    await element_click(selector["copy_response_button"], page)
    return await page.evaluate("navigator.clipboard.readText()") or "NO RESPONSE FOUND"


async def tts(text: str, page: playwright.async_api.Page, response_timeout: float = 150_000, read_aloud_timeout: float = 300_000) -> bytes:
    assert text == await chat(f"REPEAT TEXT: '{text}'", page, response_timeout=response_timeout), "Text Mismatch !"
    await element_click(selector["more_actions_button"], page)
    async with page.expect_response(
        lambda resp: "backend-api/synthesize" in resp.url and resp.status == 200, timeout=read_aloud_timeout
    ) as resp_info:
        await element_click(selector["read_aloud_button"], page)
    return await (await resp_info.value).body()


async def main():
    async with playwright.async_api.async_playwright() as pcm:
        await playwright_stealth_plugin.async_apply(pcm)
        context = await pcm.chromium.launch_persistent_context("chatgpt-data", headless=True, permissions=["clipboard-read", "clipboard-write"])
        page = await context.new_page()
        try:
            for _ in range(2):
                await page.goto(url["homepage"], wait_until="networkidle", timeout=60_000)
                if await account_check(page):
                    break
                console.print("Proceed to LOGIN !")
                email = rich.prompt.Prompt.ask("[ EMAIL ] > ", console=console)
                password = rich.prompt.Prompt.ask("[ PASSWORD ] > ", console=console)
                await login(email, password, page)
            else:
                raise Exception("LOGIN FAILURE !")
            console.print("Welcome to ChatGPT CLI !")
            while True:
                console.rule("[USER]", characters="=", style="green")
                user_text = rich.prompt.Prompt.ask("[PROMPT] > ")
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
            console.print_exception()
            console.input("PRESS ENTER TO EXIT")
        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(main())
