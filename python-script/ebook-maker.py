import os
import sys
import typing
import asyncio
import argparse
import warnings

import rich.console
import rich.traceback
import rich.progress
import rich.panel
import rich.live
import rich_argparse
import ebooklib.epub

console = rich.console.Console()
rich.traceback.install(console=console, show_locals=True)
warnings.filterwarnings("ignore")
sys.stderr = open(os.devnull, "w")

blank_line = "\n"
main_style = "magenta bold"


@typing.overload
def read_file(file_path: str, mode: typing.Literal["r"]) -> str: ...
@typing.overload
def read_file(file_path: str, mode: typing.Literal["rb"]) -> bytes: ...


@typing.overload
def write_file(file_path: str, content: str, mode: typing.Literal["w"]) -> None: ...
@typing.overload
def write_file(file_path: str, content: str, mode: typing.Literal["a"]) -> None: ...
@typing.overload
def write_file(file_path: str, content: bytes, mode: typing.Literal["wb"]) -> None: ...
@typing.overload
def write_file(file_path: str, content: bytes, mode: typing.Literal["ab"]) -> None: ...


class custom_argument_parser(argparse.ArgumentParser):
    def error(self, message: str) -> typing.NoReturn:
        self.print_help()
        console.print("\n" + "#======#_#======#" + "\n")
        console.print(message.capitalize())
        sys.exit(2)


class custom_argument_namespace(argparse.Namespace):
    folder_path: str
    file_path: str
    title: str
    language: str
    author: str
    cover_image: str


def file_path_validator(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise argparse.ArgumentTypeError(f"File doesn't exists ! [FILE PATH: '{file_path}']")
    return file_path


def folder_path_validator(folder_path: str) -> str:
    if os.path.isdir(folder_path) and len(os.listdir(folder_path)) != 0:
        raise argparse.ArgumentTypeError(f"Folder isn't empty ! [FOLDER PATH: '{folder_path}']")
    return folder_path


argument_parser = custom_argument_parser(
    prog="ebook-maker",
    formatter_class=rich_argparse.RichHelpFormatter,
    description="Make ebook from chapters effortlessly",
    epilog="No way Home !",
    add_help=False,
)

argument_parser.add_argument(
    "--file-path",
    type=str,
    metavar="FILE_PATH",
    help="File Path for novel ebook",
    required=True,
)

argument_parser.add_argument(
    "--folder-path",
    type=folder_path_validator,
    metavar="FOLDER_PATH",
    help="Folder Path for novel chapter texts",
    required=True,
)

argument_parser.add_argument("--title", type=str, help="Title for Ebook", default="[ NO TITLE ]")

argument_parser.add_argument("--author", type=str, help="Author for Ebook", default="[ NO NAME ]")

argument_parser.add_argument("--language", type=str, help="language for Ebook", default="en")

argument_parser.add_argument("--cover-image", type=file_path_validator, help="Cover Image for Ebook (jpg)", default=None)

argument_parser.add_argument(
    "--help",
    action="help",
    help="Show this help message and exit",
)

argument = argument_parser.parse_args(namespace=custom_argument_namespace())


def read_file(file_path: str, mode: str) -> str | bytes:
    with open(file_path, mode) as file:
        return file.read()


def write_file(file_path: str, content: str | bytes, mode: str) -> None:
    with open(file_path, mode) as file:
        file.write(content)


async def main() -> None:
    main_progress = rich.progress.Progress()
    main_panel = rich.panel.Panel(main_progress, style=main_style, width=60)
    live_group = rich.console.Group(blank_line, main_panel)
    with rich.live.Live(live_group, console=console, refresh_per_second=4, transient=True):
        task_id = main_progress.add_task("# TASK #", total=len(os.listdir(argument.folder_path)))
        ebook = ebooklib.epub.EpubBook()
        ebook.set_title(argument.title)
        ebook.set_language(argument.language)
        ebook.add_author(argument.author)
        if argument.cover_image:
            ebook.set_cover("cover.jpg", read_file(argument.cover_image, "rb"))
        chapters = []
        file_list = sorted(os.listdir(argument.folder_path), key=lambda f: int(os.path.splitext(f)[0].split("-")[1]))
        for file_name in file_list:
            lines = read_file(os.path.join(argument.folder_path, file_name), "r").splitlines()
            title = lines[0]
            chapter = ebooklib.epub.EpubHtml(title=title, file_name=file_name.replace(".txt", ".xhtml"))
            chapter.content = f"<h3>{title}</h3>"
            for line in lines[1:]:
                chapter.content += f"<p>{line}</p>"
            ebook.add_item(chapter)
            chapters.append(chapter)
            main_progress.advance(task_id)
        ebook.toc = chapters
        ebook.spine = ["nav"] + chapters
        ebook.add_item(ebooklib.epub.EpubNcx())
        ebook.add_item(ebooklib.epub.EpubNav())
        ebooklib.epub.write_epub(argument.file_path, ebook)


if __name__ == "__main__":
    asyncio.run(main())

# Final Version [line-length : 120]
