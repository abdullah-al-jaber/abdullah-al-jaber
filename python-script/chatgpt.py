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


class ChatGPT:
    urls = {
        "homepage": "https://chatgpt.com",
        "email_login": "https://chatgpt.com/login",
        "password_login": "https://auth.openai.com/log-in/password",
        "email_auth": "https://auth.openai.com/email-verification",
        "push_auth": "https://auth.openai.com/push-auth-verification/*",
    }

    selectors = {
        "email_login_field": "input[name='username'][type='email']",
        "password_login_field": "input[name='current-password'][type='password']",
        "email_auth_field": "input[name='code'][type='text']",
        "submit_button": "button[type='submit']",
        "prompt_box": "div[aria-label='Ask ChatGPT'][contenteditable='true'] > p",
        "send_button": "button[aria-label='Send']",
        "voice_button": "button[aria-label='Start Voice']",
        "response_box": "[data-turn-key]",
        "copy_response_button": "button[aria-label='Copy']",
        "read_aloud_button": "button[aria-label='Read aloud']",
    }

    audio_mime_type = "audio/aac"
    audio_extension = ".aac"

    clipboard_override = """
    (() => {
        window.__capturedClipboard = "";
        window.__capturedHtml = "";

        const realSetData = DataTransfer.prototype.setData;
        DataTransfer.prototype.setData = function (type, value) {
            if (type === "text/plain" || type === "text") {
                window.__capturedClipboard = String(value);
            } else if (type === "text/html") {
                window.__capturedHtml = String(value);
            }
            return realSetData.call(this, type, value);
        };
    })();
    """

    delay = 1.25
    authorize_timeout = 300_000
    response_timeout: float = 150_000
    read_aloud_timeout: float = 300_000

    def __init__(self, context: playwright.async_api.BrowserContext, page: playwright.async_api.Page):
        self.context = context
        self.page = page

    @classmethod
    async def create(cls, context: playwright.async_api.BrowserContext) -> "ChatGPT":
        page = await context.new_page()
        await page.add_init_script(cls.clipboard_override)
        await page.goto(url=cls.urls["homepage"], wait_until="load", timeout=60_000)
        return cls(context, page)

    async def account_check(self) -> bool:
        assert self.page.url != self.urls["homepage"], "Account Check Homepage Mismatch !"
        return any(cookie.get("name") == "_account" for cookie in await self.page.context.cookies())

    async def element_click(self, selector: str, delay: float = delay, parent: playwright.async_api.Locator | None = None, **options):
        element = (parent or self.page).locator(selector, **options)
        await element.wait_for(state="visible")
        await element.scroll_into_view_if_needed()
        bounding_box = await element.bounding_box()
        assert bounding_box, "Bounding Box isn't found !"
        await self.page.mouse.click(bounding_box["x"] + bounding_box["width"] / 2, bounding_box["y"] + bounding_box["height"] / 2)
        await asyncio.sleep(delay)

    async def login(self, authorize_timeout: float = authorize_timeout):
        await self.page.goto(self.urls["email_login"], wait_until="load")
        email = rich.prompt.Prompt.ask("[ EMAIL ] > ", console=console)
        await self.page.fill(self.selectors["email_login_field"], email)
        await self.element_click(self.selectors["submit_button"], has_text="Continue")

        await self.page.wait_for_url(self.urls["password_login"], wait_until="load")
        password = rich.prompt.Prompt.ask("[ PASSWORD ] > ", console=console)
        await self.page.fill(self.selectors["password_login_field"], password)
        await self.element_click(self.selectors["submit_button"], has_text="Continue")

        await self.page.wait_for_url(lambda url: url in (self.urls["email_auth"], self.urls["push_auth"]), wait_until="load")
        async with self.page.expect_navigation(timeout=authorize_timeout):
            if self.page.url == self.urls["email_auth"]:
                console.print("Email Verification Code Sent !")
                code = rich.prompt.Prompt.ask("[ CODE ] > ", console=console)
                await self.page.fill(self.selectors["email_auth_field"], code)
                await self.element_click(self.selectors["submit_button"], has_text="Continue")
            elif self.page.url == self.urls["push_auth"]:
                console.print("Authorize on Your Phone ! Quick !")

    async def chat(self, text: str, response_timeout: float = response_timeout) -> str:
        await self.page.fill(self.selectors["prompt_box"], text)
        await self.element_click(self.selectors["send_button"])
        await self.page.wait_for_selector(self.selectors["voice_button"], timeout=response_timeout)
        response = self.page.locator(selector=self.selectors["response_box"]).last
        await self.page.evaluate("window.__capturedClipboard = ''")
        await self.element_click(self.selectors["copy_response_button"], parent=response)
        output = await self.page.evaluate("window.__capturedClipboard")
        if not output or not output.strip():
            raise RuntimeError(f"RESPONSE NOT FOUND ! [PROMPT: '{text[:40]}']")
        return output

    async def tts(self, text: str, read_aloud_timeout: float = read_aloud_timeout) -> bytes:
        assert text == await self.chat(f"REPEAT TEXT: '{text}'"), "Text Mismatch !"
        async with self.page.expect_response(
            lambda resp: "backend-api/synthesize" in resp.url and resp.status == 200, timeout=read_aloud_timeout
        ) as resp_info:
            response = self.page.locator(selector=self.selectors["response_box"]).last
            await self.element_click(self.selectors["read_aloud_button"], parent=response)
        return await (await resp_info.value).body()

    async def destroy(self) -> None:
        await self.page.close()


async def main():
    async with playwright.async_api.async_playwright() as pcm:
        await playwright_stealth_plugin.async_apply(pcm)
        context = await pcm.chromium.launch_persistent_context("chatgpt-data", headless=False)
        chatgpt = await ChatGPT.create(context)
        try:
            if not await chatgpt.account_check():
                await chatgpt.login()
            console.print("Welcome to ChatGPT CLI !")
            while True:
                console.rule("[USER]", characters="=", style="green")
                user_text = rich.prompt.Prompt.ask("[PROMPT] > ")
                match user_text.split(maxsplit=1):
                    case ["/chat", message]:
                        chatgpt_text = await chatgpt.chat(message)
                        console.rule("[CHATGPT]", characters="═", style="cyan")
                        console.print(rich.markdown.Markdown(chatgpt_text))
                    case ["/tts", message]:
                        chatgpt_audio = await chatgpt.tts(message)
                        console.rule("[CHATGPT]", characters="═", style="magenta")
                        with open(rich.prompt.Prompt.ask("[AUDIO_NAME] > ") + chatgpt.audio_extension, "wb") as audio_file:
                            audio_file.write(chatgpt_audio)
                    case ["/exit"]:
                        console.print("AS YOU WISH ! MY LIFE MAY PERISH !")
                        break
                    case _:
                        console.print("INVALID ! Use /chat TEXT, /tts TEXT, /exit !")
        except Exception as error:
            await chatgpt.page.screenshot(path="error_screenshot.png", full_page=True)
            console.print("ERROR_SCREENSHOT: [cyan]error_screenshot.png[/cyan] !")
            console.print_exception()
            console.input("PRESS ENTER TO EXIT")
        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(main())
