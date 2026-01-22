import re
import os
import sys
import shutil
import zipfile
import urllib.parse

#!pip install https rich

import httpx
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
        
        content_disposition = response.headers.get("content-disposition", "")
        results = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', content_disposition)
        zip_filename = (
            urllib.parse.unquote(results.group(1))
            if results
            else (urllib.parse.urlparse(zip_url).path.split("/")[-1] or "unknown.file")
        )

        panel = rich.panel.Panel("DOWNLOAD", expand=False)
        console.print(panel)
        with rich.progress.Progress(
            rich.progress.TextColumn("{task.percentage:>3.1f}%"),
            rich.progress.TextColumn("│"),
            rich.progress.TransferSpeedColumn(),
            rich.progress.TextColumn("│"),
            rich.progress.DownloadColumn(),
            rich.progress.TextColumn("│"),
            rich.progress.TimeRemainingColumn(),
        ) as progress:
            task_id = progress.add_task("#DOWNLOAD#", total=total_size)
            with open(zip_filename, "wb") as zip_file:
                for chunk in response.iter_bytes(1024 * 1024):
                    zip_file.write(chunk)
                    progress.update(task_id, advance=len(chunk))
    return zip_filename

def extract_zip(zip_filename: str) -> str:
    zip_dirname = os.path.splitext(zip_filename)[0]
    if os.path.exists(zip_dirname):
        shutil.rmtree(zip_dirname)
    os.makedirs(zip_dirname)

    with zipfile.ZipFile(zip_filename, 'r') as zip_file:
        file_list = zip_file.infolist()

        panel = rich.panel.Panel("EXTRACT", expand=False)
        console.print(panel)
        with rich.progress.Progress(
            rich.progress.TextColumn("{task.percentage:>3.1f}%"),
            rich.progress.TextColumn("│"),
            rich.progress.TimeRemainingColumn(),
        ) as progress:
            task_id = progress.add_task("#EXTRACT#", total=len(file_list))
            for file in file_list:
                zip_file.extract(file, zip_dirname)
                progress.update(task_id, advance=1)
    return zip_dirname

def main():
    zip_url = console.input("[bold] [ZIP URL] [/bold]")
    extract_zip(download_zip(zip_url))
    panel = rich.panel.Panel("FINISH", expand=False)
    console.print(panel)

main()