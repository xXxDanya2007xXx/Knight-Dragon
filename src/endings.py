#!/usr/bin/env python3

from .sound_manager import SoundManager
from .typewriter import Typewriter
from .utils import clear_screen


def show_game_over(reason: str, sound_manager: SoundManager | None = None):
    clear_screen()

    lines = [
        "[bright_red]You lost![/bright_red]",
        "",
        reason,
        "Good luck next time!",
    ]

    with Typewriter(
        lines_for_layout=lines,
        sound_manager=sound_manager,
    ) as tw:
        for line in lines:
            tw.type(line)
        tw.wait_for_continue()

    clear_screen()


def show_victory(player_name: str, sound_manager: SoundManager | None = None):
    clear_screen()

    name = player_name if player_name else "—"

    lines = [
        "[bright_green]You won![/bright_green]",
        "",
        f"Unbelievable, [bright_magenta]{name}[/bright_magenta]!",
        "Congratulations!"
    ]

    with Typewriter(
        lines_for_layout=lines,
        sound_manager=sound_manager,
    ) as tw:
        for line in lines:
            tw.type(line)
        tw.wait_for_continue()

    clear_screen()
