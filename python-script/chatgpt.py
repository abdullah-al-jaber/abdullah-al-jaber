import playwright.sync_api
import playwright_stealth_plugin

text_box_selector = "div#prompt-textarea > p"
chat_button_selector = "button[aria-label='Send prompt']"
voice_button_selector = "button[aria-label='Start Voice']"
chat_box_selector = "[data-message-author-role='assistant']"


def chat(text: str, page: playwright.sync_api.Page) -> str:
    page.wait_for_selector(text_box_selector)
    page.fill(text_box_selector, text)
    page.wait_for_selector(chat_button_selector)
    page.click(chat_button_selector)
    page.wait_for_selector(voice_button_selector)
    page.wait_for_selector(chat_box_selector)
    return page.locator(chat_box_selector).nth(-1).inner_text().strip() or "NO RESPONSE FOUND"


with playwright.sync_api.sync_playwright() as pm:
    playwright_stealth_plugin.sync_apply(pm)
    context = pm.chromium.launch_persistent_context("data", headless=False)
    page = context.new_page()
    page.goto("https://chatgpt.com/", wait_until="load")
    print(chat("What is the capital of France ?", page))
    print(chat("What is the capital of Germany ?", page))
    print(chat("What is the capital of Italy ?", page))
    print(chat("What is the capital of Spain ?", page))
    input("Press enter to exit !")
    context.close()
