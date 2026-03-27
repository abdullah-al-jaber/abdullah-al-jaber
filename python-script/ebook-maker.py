import os
import sys

import ebooklib
import rich.console
import rich.prompt
import rich.progress
import rich.panel
import rich.live
import rich.traceback

console = rich.console.Console()
rich.traceback.install(console=console, show_locals=True)
sys.stderr = open("/dev/null", "w")


def download_zip(zip_url: str) -> str:
    progress = rich.progress.Progress(
        rich.progress.TaskProgressColumn(),
        rich.progress.TextColumn("●"),
        rich.progress.TransferSpeedColumn(),
        rich.progress.TextColumn("●"),
        rich.progress.TimeRemainingColumn(),
    )
    panel = rich.panel.Panel(progress, title="[ DOWNLOAD ]", expand=False, width=40)
    with rich.live.Live(panel, console=console, refresh_per_second=10):
        with httpx.stream("GET", zip_url) as response:
            total = int(response.headers.get("Content-Length", 0))
            task = progress.add_task("# DOWNLOAD #", total=total)
            zip_file_name = urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(zip_url).path))
            with open(zip_file_name, "wb") as zip_file:
                for chunk in response.iter_bytes():
                    zip_file.write(chunk)
                    progress.update(task, advance=len(chunk))
    return zip_file_name


def extract_zip(zip_file_name: str) -> str:
    progress = rich.progress.Progress(
        rich.progress.TaskProgressColumn(),
        rich.progress.TextColumn("●"),
        rich.progress.TransferSpeedColumn(),
        rich.progress.TextColumn("●"),
        rich.progress.TimeRemainingColumn(),
        expand=False,
    )
    panel = rich.panel.Panel(progress, title="[ EXTRACT ]", expand=False, width=40)
    with rich.live.Live(panel, console=console, refresh_per_second=10):
        with zipfile.ZipFile(zip_file_name, "r") as zip_file:
            task = progress.add_task("# EXTRACT #", total=len(zip_file.infolist()))
            zip_folder_name = f"{zip_file_name}.extract"
            os.mkdir(zip_folder_name)
            for info in zip_file.infolist():
                zip_file.extract(info, path=zip_folder_name)
                progress.update(task, advance=1)
    return zip_folder_name


def main():
    zip_url = rich.prompt.Prompt.ask(" [ ZIP URL ] > ")
    zip_file_name = download_zip(zip_url)
    zip_folder_name = extract_zip(zip_file_name)
    panel = rich.panel.Panel(f"OUTPUT: [cyan]{zip_folder_name}[/cyan]", title="[ DONE ]", expand=False)
    console.print(panel)


if __name__ == "__main__":
    main()
