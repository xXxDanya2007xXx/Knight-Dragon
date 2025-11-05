#!/usr/bin/env python3

from .ui import Typewriter
from .sound_manager import SoundManager
from .utils import clear_screen


def show_game_over(reason, sound_manager: SoundManager | None = None):
    clear_screen()

    if isinstance(reason, (list, tuple)):
        reason_lines = list(reason)
    elif reason is None:
        reason_lines = []
    else:
        reason_lines = [str(reason)]

    lines = [
        "[bright_red]Ты проиграл... :([/bright_red]",
        "",
        *reason_lines,
        "",
        "Повезет в следующий раз!",
    ]
    with Typewriter(lines_for_layout=lines, sound_manager=sound_manager) as tw:
        for line in lines:
            tw.type(line)
        tw.wait_for_continue()


def show_victory(player_name: str, sound_manager: SoundManager | None = None):
    clear_screen()

    name = player_name if player_name else "Knight"
    lines = [
        "[bright_green]Ты выиграл! :D[/bright_green]",
        "",
        f"Невероятно, [bright_magenta]{name}[/bright_magenta]!"
    ]

    with Typewriter(lines_for_layout=lines, sound_manager=sound_manager) as tw:
        for line in lines:
            tw.type(line)
        tw.wait_for_continue()
