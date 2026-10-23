import re
import os
import sys
import shutil
import signal
import collections
import concurrent.futures

import gdown
import rich.live
import rich.panel
import rich.table
import rich.prompt
import rich.console
import rich.progress
import rich.traceback

DRIVE_FOLDER_ID = "PASTE_DRIVE_FOLDER_ID"
LOCAL_FOLDER_NAME = "google_drive"
MAX_WORKERS = 8

COOKIE = "PASTE_COOKIE"

console = rich.console.Console()
rich.traceback.install(console=console)

def handle_interrupt(signum, frame):
    console.line()
    console.print(rich.panel.Panel(
        rich.align.Align("KEYBOARD INTERRUPT", align="center"),
        style="bold",
        border_style="red",
    ))
    os._exit(1)

signal.signal(signal.SIGINT, handle_interrupt)

console.print(rich.panel.Panel(
    rich.align.Align("FETCHING LOCAL ENTRIES", align="center"),
    style="bold",
    border_style="magenta",
))
os.makedirs(LOCAL_FOLDER_NAME, exist_ok=True)
local_entries = set()
for root, dirs, files in os.walk(LOCAL_FOLDER_NAME, topdown=False):
    for name in files:
        full_path = os.path.join(root, name)
        rel_path = os.path.relpath(full_path, LOCAL_FOLDER_NAME)
        local_entries.add(os.path.normpath(rel_path))
    if root != LOCAL_FOLDER_NAME and not os.listdir(root):
        os.rmdir(root)

def sanitize_path(path):
    parts = path.split("/")
    safe_parts = [re.sub(r'[\\/:*?"<>|]', "_", part) for part in parts]
    return "/".join(safe_parts)

console.print(rich.panel.Panel(
    rich.align.Align("FETCHING DRIVE ENTRIES", align="center"),
    style="bold",
    border_style="cyan",
))
drive_entries = gdown.download_folder(id=DRIVE_FOLDER_ID, skip_download=True, quiet=True, use_cookies=COOKIE)
drive_files = {
    os.path.normpath(sanitize_path(re.sub(r"[\r\n]+", "", path).replace("\\", "/"))): file_id
    for file_id, path, local_path in drive_entries
}

MISSING = sorted(path for path in drive_files if path not in local_entries)
STALE = sorted(path for path in local_entries if path not in drive_files)
SYNCED = sorted(path for path in drive_files if path in local_entries)

console.line()
folder_changes = collections.defaultdict(list)

for path in MISSING:
    folder = os.path.dirname(path) or "."
    folder_changes[f"[bold]⟨●⟩[/bold] '{folder}'"].append(("+", os.path.basename(path)))

for path in STALE:
    folder = os.path.dirname(path) or "."
    folder_changes[f"[bold]⟨●⟩[/bold] '{folder}'"].append(("-", os.path.basename(path)))

if len(folder_changes) == 0:
    console.print("[bold] WE DID EVERYTHING WE COULD [/bold]")
    sys.exit(0)

for folder in sorted(folder_changes):
    console.print(folder)
    table = rich.table.Table(show_header=True)
    table.add_column("STATE", justify="center")
    table.add_column("FILE NAME")
    for marker, filename in sorted(folder_changes[folder], key=lambda x: x[1]):
        style = "green" if marker == "+" else "red"
        table.add_row(f"[{style}]{marker}[/{style}]", filename)
    console.print(table)
    console.print()

SYNC_MODE = rich.prompt.Prompt.ask(
    "SELECT [bold]SYNC MODE[/bold]",
    choices=["ADD", "REMOVE", "BOTH"],
    default="BOTH",
    case_sensitive=False,
)

sync_rows = collections.deque(maxlen=10)

progress = rich.progress.Progress(
    rich.progress.TextColumn("[bold]{task.description}"),
    rich.progress.BarColumn(bar_width=None),
    rich.progress.MofNCompleteColumn(),
    rich.progress.TimeRemainingColumn(),
)
progress_panel = rich.panel.Panel(progress, expand=True)

MISSING_OPS = MISSING if SYNC_MODE in ("ADD", "BOTH") else []
STALE_OPS = STALE if SYNC_MODE in ("REMOVE", "BOTH") else []
TOTAL_OPS = len(MISSING_OPS) + len(STALE_OPS)

task = progress.add_task("[bold]SYNC[/bold]", total=TOTAL_OPS)

def download_file(path):
    file_id = drive_files[path]
    dest_path = os.path.join(LOCAL_FOLDER_NAME, path)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    gdown.download(id=file_id, output=dest_path, quiet=True, use_cookies=COOKIE)
    return "+", path

def remove_file(path):
    dest_path = os.path.join(LOCAL_FOLDER_NAME, path)
    os.remove(dest_path)
    return "-", path


with rich.live.Live(
    progress_panel,
    console=console,
    refresh_per_second=10,
) as live:
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_file, path): path for path in MISSING_OPS}
        futures.update({executor.submit(remove_file, path): path for path in STALE_OPS})

        for future in concurrent.futures.as_completed(futures):
            marker, path = future.result()
            style = "green" if marker == "+" else "red"
            sync_rows.append((f"[{style}]{marker}[/{style}]", path))
            sync_table = rich.table.Table(show_header=False)
            sync_table.add_column("ACTION", justify="center")
            sync_table.add_column("FILE NAME")
            sync_table = rich.table.Table(show_header=False)
            for marker, path in sync_rows:
                sync_table.add_row(marker, path)
            progress.advance(task)
            renderable = rich.console.Group(sync_table, progress_panel) if sync_table.row_count > 0 else progress_panel
            live.update(renderable)