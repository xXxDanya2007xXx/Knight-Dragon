#!/usr/bin/env python3

from ..utils import clear_screen
from ..ui import Typewriter
from ..sound_manager import SoundManager


def run(player_name: str, sound_manager: SoundManager | None = None):
    clear_screen()

    name = player_name if player_name else "Knight"
    lines = [
        f"Привет, [bright_magenta]{name}[/bright_magenta]!",
        "",
        "Это очень интересная история, поэтому слушай внимательно...",
        "",
        "Итак...",
        "",
        ".",
        ".",
        ".",
    ]

    with Typewriter(lines_for_layout=lines, sound_manager=sound_manager) as tw:
        for line in lines:
            tw.type(line)
        tw.wait_for_continue()
