import re
import sys
import asyncio
import pathlib
import argparse

import rich.console
import rich.progress
import rich.panel
import rich.live
import rich.traceback
import rich_argparse
import playwright.async_api
import playwright_stealth_plugin

console = rich.console.Console()
rich.traceback.install(console=console, show_locals=True)
sys.stderr = open("/dev/null", "w")

url = {
    "homepage": "https://gemini.google.com/app",
}

selector = {
    "prompt_box": "div[contenteditable='true'][aria-label='Enter a prompt for Gemini'] > p",
    "submit_button": "button[aria-label='Send message']",
    "voice_button": "button[aria-label='Dictate (^⇧D)']",
    "copy_button": "infinite-scroller > .conversation-container:last-of-type copy-button",
}

CHAT_INSTRUCTION = (
    "Translate Texts Given During Chat Into English. Only Give Translation In Response. Understood ?"
)


async def element_click(selector: str, page: playwright.async_api.Page, delay: float = 1.25):
    element = page.locator(selector)
    await element.wait_for(state="visible")
    await element.scroll_into_view_if_needed()
    bounding_box = await element.bounding_box()
    assert bounding_box, "Bounding Box isn't found !"
    await page.mouse.click(bounding_box["x"] + bounding_box["width"] / 2, bounding_box["y"] + bounding_box["height"] / 2)
    await asyncio.sleep(delay)


async def chat_up(text: str, page: playwright.async_api.Page, response_timeout: float = 150_000) -> str:
    await page.fill(selector["prompt_box"], text)
    await element_click(selector["submit_button"], page)
    await page.wait_for_selector(selector["voice_button"], timeout=response_timeout)
    await element_click(selector["copy_button"], page)
    return await page.evaluate("navigator.clipboard.readText()")


class ChatBot:
    def __init__(self, context: playwright.async_api.BrowserContext, page: playwright.async_api.Page):
        self.context = context
        self.page = page

    @classmethod
    async def create(cls, context: playwright.async_api.BrowserContext) -> "ChatBot":
        page = await context.new_page()
        await page.goto(url=url["homepage"], wait_until="domcontentloaded", timeout=60_000)
        return cls(context, page)

    async def chat(self, text: str):
        return await chat_up(text, self.page, response_timeout=120_000 + len(text) * 2)

    async def destroy(self) -> None:
        await self.page.close()


async def main():
    argument_parser = argparse.ArgumentParser(
        description="Translate with Thunders From Gemini",
        formatter_class=rich_argparse.RichHelpFormatter,
    )
    argument_parser.add_argument(
        "--input-folder",
        type=pathlib.Path,
        required=True,
        help="Folder To Get Input Files",
    )
    argument_parser.add_argument(
        "--output-folder",
        type=pathlib.Path,
        required=True,
        help="Folder To Put Output Files",
    )
    argument_parser.add_argument(
        "--worker-count",
        type=int,
        default=3,
        help="Number Worker (Trade Stability For Speed)",
    )
    arguments = argument_parser.parse_args()

    if not arguments.input_folder.is_dir():
        argument_parser.error(f"Input Folder Don't Exist ! [FOLDER: {arguments.input_folder}]")

    text_files = list(arguments.input_folder.rglob("*.txt"))
    text_files.sort(key=lambda path: ([int(number) for number in re.findall(r"\d+", path.name)], path.name))

    files_list = [[] for _ in range(min(arguments.worker_count, len(text_files)))]
    for index, text_file in enumerate(text_files):
        files_list[index % arguments.worker_count].append(text_file)

    async with playwright.async_api.async_playwright() as pcm:
        await playwright_stealth_plugin.async_apply(pcm)
        context = await pcm.chromium.launch_persistent_context("gemini-data", headless=False, permissions=["clipboard-read", "clipboard-write"])
        chat_bots = await asyncio.gather(*(ChatBot.create(context) for _ in files_list))
        await asyncio.gather(*(chatbot.chat(CHAT_INSTRUCTION) for chatbot in chat_bots))

        progress = rich.progress.Progress(
            rich.progress.TextColumn("[TRANSLATION]"),
            rich.progress.MofNCompleteColumn(),
            rich.progress.TimeElapsedColumn(),
            rich.progress.TimeRemainingColumn(),
            console=console,
        )

        async def translate_work_list(chatbot, files, task_id):
            for text_file in files:
                translation = await chatbot.chat(text_file.read_text(encoding="utf-8"))
                target = arguments.output_folder / text_file.relative_to(arguments.input_folder)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(translation, encoding="utf-8")
                progress.advance(task_id)

        with rich.live.Live(rich.panel.Panel(progress, expand=False), console=console):
            tasks = [
                translate_work_list(chatbot, files, progress.add_task("TRANSLATE", total=len(files))) for chatbot, files in zip(chat_bots, files_list)
            ]
            await asyncio.gather(*tasks)

        await asyncio.gather(*(chatbot.destroy() for chatbot in chat_bots))
        await context.close()


if __name__ == "__main__":
    asyncio.run(main())
