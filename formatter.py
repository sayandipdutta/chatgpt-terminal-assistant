from rich import print
from rich.console import Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from typing import Literal, Optional, TypeAlias

from usage_tracker import load_records

LINE_BR = Text()
WELCOME = Text(
    "Welcome to ChatGPT Terminal Assistant", style="bold blue", justify="center"
)
INSTRUCTIONS = Group(
    Text.assemble("Enter your question after ", (">", "bold red"), justify="center"),
    Text(
        "If you want to exit, just hit enter without entering any text.",
        justify="center",
    ),
)

Theme: TypeAlias = Literal["gruvbox-light", "gruvbox-dark"]


def format_content(content: str, tokens: int, theme: Theme) -> Panel:
    return Panel(
        Markdown(
            content,
            code_theme=theme,
            inline_code_theme=theme,
        ),
        title="[bold blue]Assistant",
        subtitle=f"[red]consumed {tokens=}",
        padding=(1, 1),
        border_style="green"
    )


def welcome(history: Optional[int]=None):
    _, last_session_details = load_records()
    time, tokens, cost = last_session_details.decode(encoding="utf-8").split(",")
    fcost = float(cost)
    cost = f"\N{DOLLAR SIGN}{fcost:.5f}"
    last_sess = Group(
        Text(f"Last session ({time}): tokens: {tokens}, cost: {cost}", justify="center"),
    )
    max_hist = []
    if history is not None:
        max_hist = [Text(f"Conversation limit: {history}", justify="center", style="italic")]
    print(
        Panel(
            Group(WELCOME, last_sess, LINE_BR, INSTRUCTIONS, *max_hist),
            title="[green]Welcome",
        )
    )

def thank_you(*info: str | None):
    messages: list[Text] = []
    for i in info:
        if i is None:
            continue
        messages.append(Text(i, justify="center"))
    messages.append(Text("Session ended.", justify="center"))
    print(Panel(Group(*messages), border_style="red"))
