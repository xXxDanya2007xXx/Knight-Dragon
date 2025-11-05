#!/usr/bin/env python3

import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def clear_screen():
    _ = os.system("cls" if os.name == "nt" else "clear")


def show_placeholder():
    console = Console()
    clear_screen()
    panel = Panel.fit(
        Text(
            "В разработке. Нажмите Enter, чтобы вернуться в главное меню...",
            style="bright_white",
            justify="center"
        ), border_style="bright_black"
    )
    console.print(panel, justify="center")
    _ = input()
