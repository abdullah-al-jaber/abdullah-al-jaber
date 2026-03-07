import asyncio
import playwright.async_api
import playwright_stealth_plugin

text_box_selector = "div#prompt-textarea > p"
chat_button_selector = "button[aria-label='Send prompt']"
voice_button_selector = "button[aria-label='Start Voice']"
chat_box_selector = "[data-message-author-role='assistant']"
more_button_selector = "article[data-turn-id^='request-WEB']:last-of-type button[aria-label='More actions']"
read_button_selector = "[data-radix-popper-content-wrapper] div[role='menuitem'][aria-label='Read aloud']"


async def chat(text: str, page: playwright.async_api.Page) -> str:
    await page.wait_for_selector(text_box_selector)
    await page.fill(text_box_selector, text)
    await page.wait_for_selector(chat_button_selector)
    await page.click(chat_button_selector)
    await page.wait_for_selector(voice_button_selector)
    await page.wait_for_selector(chat_box_selector)
    await asyncio.sleep(2)
    return (await page.locator(chat_box_selector).nth(-1).inner_text()).strip() or "NO RESPONSE FOUND"


async def tts(text: str, page: playwright.async_api.Page) -> bytes:
    await chat(text, page)
    await page.wait_for_selector(more_button_selector)
    await page.click(more_button_selector)
    async with page.expect_response(lambda resp: "backend-api/synthesize" in resp.url and resp.status == 200) as resp_info:
        await page.wait_for_selector(read_button_selector)
        await page.click(read_button_selector)
    response = await resp_info.value
    audio_bytes = await response.body()
    return audio_bytes


def save_audio(audio_bytes: bytes, filename: str):
    with open(filename, "wb") as f:
        f.write(audio_bytes)


async def main():
    async with playwright.async_api.async_playwright() as pm:
        await playwright_stealth_plugin.async_apply(pm)
        context = await pm.chromium.launch_persistent_context("data", headless=False)
        page = await context.new_page()
        await page.goto("https://chatgpt.com/", wait_until="load")
        story = await chat("Tell me a story !!", page)
        await chat("Repeat what say from now on !! Nothing else !!", page)
        audio_bytes = await tts(story, page)
        save_audio(audio_bytes, "output.acc")
        input("Press enter to exit !")
        await context.close()


if __name__ == "__main__":
    asyncio.run(main())
