import re
import os
import sys
import zipfile
import urllib.parse

import httpx
import rich.console
import rich.progress
import rich.panel
import rich.live
import rich.traceback

console = rich.console.Console()
rich.traceback.install(console=console, show_locals=True)
sys.stderr = open("/dev/null", "w")

blank_line = "\n"
separator = "●"


def download_zip(zip_url: str) -> str:
    progress = rich.progress.Progress(
        rich.progress.TaskProgressColumn(),
        rich.progress.TextColumn(separator),
        rich.progress.TransferSpeedColumn(),
        rich.progress.TextColumn(separator),
        rich.progress.TimeRemainingColumn(),
    )
    panel = rich.panel.Panel(progress, title="[ DOWNLOAD ]")
    group = rich.console.Group(blank_line, panel, blank_line)
    with rich.live.Live(group, console=console, refresh_per_second=10):
        with httpx.stream("GET", zip_url) as response:
            total = int(response.headers.get("Content-Length", 0))
            task = progress.add_task("# DOWNLOAD #", total=total)
            zip_file_name = urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(zip_url).path))
            with open(zip_file_name, "wb") as zip_file:
                for chunk in response.iter_bytes():
                    zip_file.write(chunk)
                    progress.update(task, advance=len(chunk))
    return zip_file_name


def extract_zip(zip_name: str) -> str:
    progress = rich.progress.Progress(
        rich.progress.TaskProgressColumn(),
        rich.progress.TextColumn(separator),
        rich.progress.TransferSpeedColumn(),
        rich.progress.TextColumn(separator),
        rich.progress.TimeRemainingColumn(),
    )
    panel = rich.panel.Panel(progress, title="[ EXTRACT ]")
    group = rich.console.Group(blank_line, panel, blank_line)
    with rich.live.Live(group, console=console, refresh_per_second=10):
        with zipfile.ZipFile(zip_name, "r") as zip_file:
            task = progress.add_task("# EXTRACT #", total=len(zip_file.infolist()))
            zip_folder_name = os.path.splitext(zip_name)[0]
            for info in zip_file.infolist():
                zip_file.extract(info, path=zip_folder_name)
                progress.update(task, advance=1)
    return zip_folder_name


def main():
    zip_url = console.input(" [ ZIP URL ] ")
    zip_name = download_zip(zip_url)
    zip_folder = extract_zip(zip_name)
    console.print(rich.panel.Panel(f"OUTPUT: {zip_folder}", title="[ DONE ]"))


if __name__ == "__main__":
    main()
