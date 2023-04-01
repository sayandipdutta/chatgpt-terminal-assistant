from rich.markdown import Markdown
from rich.panel import Panel

from typing import Literal, TypeAlias

Theme: TypeAlias = Literal['gruvbox-light', 'gruvbox-dark']


def format_content(content: str, tokens: int, theme: Theme) -> Panel:
    return Panel(
        Markdown(
            content,
            code_theme=theme,
            inline_code_theme=theme,
        ),
        title="Assistant",
        subtitle=f"consumed {tokens=}"
    )
