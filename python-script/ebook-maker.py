import re
import os
import random
import typing
import asyncio

import bs4
import ebooklib.epub

## CONFIG ##
TITLE = "Nobody Knows Title !?"
AUTHOR = "Forgetful Author"
DESCRIPTION = """
 Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus.
 Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor.
 Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi.
"""
COVER_IMAGE_PATH = os.path.join(".BookCover", random.choice(os.listdir(".BookCover")))

FOLDER_PATH = "NOVEL_TEXT_FILES"
FILE_PATH = "EBOOK.epub"

### MOD HERE
# COVER_IMAGE_PATH = "cover.jpg"
# FOLDER_PATH = "FN"


@typing.overload
def read_file(file_path: str, mode: typing.Literal["r"]) -> str: ...
@typing.overload
def read_file(file_path: str, mode: typing.Literal["rb"]) -> bytes: ...


@typing.overload
def write_file(file_path: str, content: str, mode: typing.Literal["word"]) -> None: ...
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
    epub_book.set_unique_metadata("DC", "description", DESCRIPTION)
    epub_book.set_cover(COVER_IMAGE_PATH, read_file(COVER_IMAGE_PATH, "rb"))
    file_names = sorted(os.listdir(FOLDER_PATH), key=number)
    chapters = []
    for idx, file_name in enumerate(file_names):
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
        chapter.content = "<br/>" * 3 + str(soup) + "<p> ㅤ </p>"
        epub_book.add_item(chapter)
        chapters.append(chapter)
    epub_book.toc = chapters
    epub_book.spine = ["nav"] + chapters
    ebooklib.epub.write_epub(FILE_PATH, epub_book)


if __name__ == "__main__":
    asyncio.run(main())
