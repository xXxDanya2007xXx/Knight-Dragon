#!/usr/bin/env python3

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
import os


def clear_screen():
    _ = os.system("cls" if os.name == "nt" else "clear")


def show_placeholder():
    console = Console()

    clear_screen()
    panel = Panel.fit(Text("Press Enter to go back...",
                      style="bold white", justify="center"),
                      border_style="bold black")
    console.print(panel, justify="center")
    _ = input()


def show_help_message():
    console = Console()

    console.print()
    help_text = (
        "Use [bright_white]↑ ↓[/bright_white] to navigate, "
        "[bright_white]Enter[/bright_white] to select, "
        "[bright_red]q[/bright_red] - quit the game"
    )
    console.print(help_text, justify="center")
