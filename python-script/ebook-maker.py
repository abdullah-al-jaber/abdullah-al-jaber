import re
import os
import typing
import asyncio

import bs4
import ebooklib.epub

## CONFIG ##
TITLE = "NO TITLE"
AUTHOR = "NO AUTHOR"
DESCRIPTION = """
NO DESCRIPTION
"""
LANGUAGE = "en"
COVER_IMAGE_PATH = "NONE"

FILE_PATH = "EBOOK.epub"
FOLDER_PATH = "TEXT"


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


def read_file(file_path: str, mode: str) -> str | bytes:
    with open(file_path, mode) as file:
        return file.read()


def write_file(file_path: str, content: str | bytes, mode: str) -> None:
    with open(file_path, mode) as file:
        file.write(content)


def number(file_name: str) -> int:
    match = re.search(r"\d+", file_name)
    return int(match.group()) if match else -1


async def main() -> None:
    epub_book = ebooklib.epub.EpubBook()
    epub_book.set_title(TITLE)
    epub_book.add_author(AUTHOR)
    epub_book.set_language(LANGUAGE)
    epub_book.set_unique_metadata("DC", "description", DESCRIPTION)
    epub_book.set_cover("cover.jpg", read_file(COVER_IMAGE_PATH, "rb")) if COVER_IMAGE_PATH != "NONE" else None
    file_names = sorted(os.listdir(FOLDER_PATH), key=number)
    chapters = []
    for file_name in file_names:
        lines = read_file(os.path.join(FOLDER_PATH, file_name), "r").splitlines()
        chapter = ebooklib.epub.EpubHtml(title=lines[0], file_name=file_name.replace(".txt", ".xhtml"))
        soup = bs4.BeautifulSoup("", "html.parser")
        h3 = soup.new_tag("h3")
        h3.string = lines[0]
        soup.append(h3)
        for line in lines[1:]:
            p = soup.new_tag("p")
            p.string = line
            soup.append(p)
        chapter.content = soup.prettify()
        epub_book.add_item(chapter)
        chapters.append(chapter)
    epub_book.toc = chapters
    epub_book.spine = ["nav"] + chapters
    epub_book.add_item(ebooklib.epub.EpubNcx())
    epub_book.add_item(ebooklib.epub.EpubNav())
    ebooklib.epub.write_epub(FILE_PATH, epub_book)


if __name__ == "__main__":
    asyncio.run(main())

# Final Version [line-length : 150]
