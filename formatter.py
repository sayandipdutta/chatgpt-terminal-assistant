from datetime import datetime
from rich import print
from rich.console import Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from typing import Literal, TypeAlias

from usage_tracker import load_records

LINE_BR = Text()
Theme: TypeAlias = Literal["gruvbox-light", "gruvbox-dark"]


def format_content(content: str, tokens: int, theme: Theme) -> Panel:
    return Panel(
        Markdown(
            content,
            code_theme=theme,
            inline_code_theme=theme,
        ),
        title="Assistant",
        subtitle=f"consumed {tokens=}",
    )


def welcome():
    name = Text("Welcome to ChatGPT Terminal Assistant", style="bold blue", justify="center")
    instructions = Group(
        Text.assemble("Enter your question after ", (">", "bold red"), justify="center"),
        Text("If you want to exit, just hit enter without entering any text.", justify="center")
    )
    _, last_session_details = load_records()
    time, tokens, cost = last_session_details.decode(encoding='utf-8').split(',')
    fcost = float(cost)
    cost = f"\N{DOLLAR SIGN}{fcost:.5f}"
    last_sess = Group(
        Text("Last session usage details:", style="bold", justify="center"),
        Text(f"{time = }, {tokens = }, {cost = }", justify="center")
    )
    print(
        Panel(Group(name, LINE_BR, instructions, LINE_BR, last_sess), title="[green]Welcome")
    )
