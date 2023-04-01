from abc import ABC, abstractmethod
from typing import Iterator, Literal

from rich import print
from rich.panel import Panel
from rich.markdown import Markdown

BLOCK_INDICATOR: Literal["```\n"] = "```\n"


class Renderable(ABC):
    @abstractmethod
    def render(self) -> Panel:
        pass


class Text(Renderable):
    def __init__(self, data: str) -> None:
        self.data = data

    def render(self) -> Panel:
        # TODO: Format keywords differently using re
        return Panel(self.data)


class Code(Renderable):
    def __init__(self, data: str) -> None:
        self.data = data

    def render(self) -> Panel:
        return Panel(self.data)


def make_markdown(
    content: str,
    theme: Literal["solarized-light", "solarized-dark"] = "solarized-light",
) -> Panel:
    return Panel(Markdown(content, code_theme=theme))


def content_parser(content: str) -> Iterator[Renderable]:
    # FIX: Write tests to check the function
    code_block: list[str] = []
    text_block: list[str] = []
    code_block_running: bool
    if code_block_running := content.startswith(BLOCK_INDICATOR):
        _, content = content.split(BLOCK_INDICATOR, 1)
    block = code_block if code_block_running else text_block
    for line in content.splitlines(keepends=True):
        if line == BLOCK_INDICATOR:
            if code_block_running:
                yield Code("".join(block))
            else:
                yield Text("".join(block))
            code_block_running = not code_block_running
            block.clear()
            continue
        block.append(line)
    if block:
        b = "".join(block)
        del block
        yield Code(b) if code_block_running else Text(b)
