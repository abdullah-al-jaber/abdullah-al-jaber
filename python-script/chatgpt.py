import asyncio
import rich.traceback
import playwright.async_api
import playwright_stealth_plugin

# SCRIPT NEEDS TO RUN IN UBUNTU OR DEBIAN
# CHAT - LOGIN / ANONYMOUS , TTS - LOGIN ONLY
rich.traceback.install(show_locals=True)

text_box_selector = "div#prompt-textarea > p"
prompt_button_selector = "button[aria-label='Send prompt']"
voice_button_selector = "button[aria-label='Start Voice']"
chat_article_selector = "[data-message-author-role='assistant']"
more_button_selector = "article[data-turn-id^='request-WEB']:last-of-type button[aria-label='More actions']"
read_button_selector = "[data-radix-popper-content-wrapper] div[role='menuitem'][aria-label='Read aloud']"


async def chat(text: str, page: playwright.async_api.Page) -> str:
    await page.wait_for_selector(text_box_selector)
    await page.fill(text_box_selector, text)
    await asyncio.sleep(min(len(text) * 0.05, 5))
    await page.wait_for_selector(prompt_button_selector)
    await page.click(prompt_button_selector)
    await page.wait_for_selector(voice_button_selector)
    await page.wait_for_selector(chat_article_selector)
    return (await page.locator(chat_article_selector).nth(-1).inner_text()).strip() or "NO RESPONSE FOUND"


async def tts(text: str, page: playwright.async_api.Page) -> bytes:
    await chat(f"Please repeat the following text: {text}", page)
    await page.wait_for_selector(more_button_selector)
    await page.click(more_button_selector)
    async with page.expect_response(lambda resp: "backend-api/synthesize" in resp.url and resp.status == 200) as resp_info:
        await page.wait_for_selector(read_button_selector)
        await page.click(read_button_selector)
    response = await resp_info.value
    audio_bytes = await response.body()
    return audio_bytes


async def main():
    async with playwright.async_api.async_playwright() as pm:
        await playwright_stealth_plugin.async_apply(pm)
        context = await pm.chromium.launch_persistent_context("data", headless=False)
        page = await context.new_page()
        try:
            await page.goto("https://chatgpt.com/", wait_until="load")
            rich.print(f'CHAT: {await chat("Tell me joke ! One line !", page)}')
            # open("audio.aac", "wb").write(await tts("THIS IS A TEST", page))
            # rich.print("TTS: Play audio.aac to hear the result.")
            input("[PRESS ENTER TO EXIT]")
        except Exception as error:
            await page.screenshot(path="error_screenshot.png", full_page=True)
            rich.print("SCREENSHOT SAVED: error_screenshot.png")
            raise error
        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(main())
