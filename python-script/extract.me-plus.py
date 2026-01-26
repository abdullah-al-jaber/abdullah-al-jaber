import re
import os
import sys
import shutil
import zipfile
import urllib.parse

#!pip install https rich requests-toolbelt

import httpx
import requests_toolbelt.utils
import rich.traceback
import rich.console
import rich.progress
import rich.panel

rich.traceback.install()
console = rich.console.Console()


def download_zip(zip_url: str) -> str:
    with httpx.stream("GET", zip_url) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("content-length") or 0)
        zip_filename = (
            content_disposition.get_filename(response.headers.get("content-disposition"))
            or urllib.parse.urlparse(zip_url).path.split("/")[-1]
            or "archive.bin"
        )
        console.print(rich.panel.Panel("DOWNLOAD", expand=False))
        with rich.progress.Progress(
            rich.progress.TextColumn("{task.percentage:>3.1f}%"),
            rich.progress.TextColumn("•"),
            rich.progress.TransferSpeedColumn(),
            rich.progress.TextColumn("•"),
            rich.progress.DownloadColumn(),
            rich.progress.TextColumn("•"),
            rich.progress.TimeRemainingColumn(),
            console=console,
            expand=False,
        ) as progress:
            task_id = progress.add_task("#DOWNLOAD#", total=total_size)
            with open(zip_filename, "wb") as zip_file:
                for chunk in response.iter_bytes(1024 * 1024):
                    zip_file.write(chunk)
                    progress.advance(task_id, advance=len(chunk))
    return zip_filename


def extract_zip(zip_filename: str) -> str:
    zip_dirname = os.path.splitext(zip_filename)[0]
    shutil.rmtree(zip_dirname, ignore_errors=True)
    os.makedirs(zip_dirname)
    with zipfile.ZipFile(zip_filename, "r") as zip_file:
        zip_entries = zip_file.infolist()
        console.print(rich.panel.Panel("EXTRACT", expand=False))
        with rich.progress.Progress(
            rich.progress.TextColumn("{task.percentage:>3.1f}%"),
            rich.progress.TextColumn("•"),
            rich.progress.TimeRemainingColumn(),
            console=console,
            expand=False,
        ) as progress:
            task_id = progress.add_task("#EXTRACT#", total=len(file_list))
            for zip_entry in zip_entries:
                zip_file.extract(zip_entry, zip_dirname)
                progress.advance(task_id)
    return zip_dirname


def main():
    zip_url = console.input("[bold] [ZIP URL] [/bold]")
    extract_zip(download_zip(zip_url))
    console.print(rich.panel.Panel("FINISH", expand=False))


if __name__ == "__main__":
    main()()
