#!/usr/bin/env python3

from ..sound_manager import SoundManager
from ..typewriter import Typewriter
from ..utils import clear_screen


class IntroStory:
    def __init__(self, sound_manager: SoundManager | None = None):
        self.sound_manager: SoundManager | None = sound_manager

    def show(self, player_name: str):
        clear_screen()
        name = player_name if player_name else "—"

        lines = [
            f"Your name is [bright_magenta]{name}[/bright_magenta]?",
            "",
            "Yeah, whatever.",
            "So...",
            "",
            "Once upon a time...",
            "...",
            "...",
            "...",
        ]

        with Typewriter(
            lines_for_layout=lines,
            title="Prologue",
            sound_manager=self.sound_manager,
        ) as tw:
            tw.type(lines[0], pause_after=1.0)
            tw.type(lines[1])
            tw.type(lines[2], pause_after=0.5)
            tw.type(lines[3], pause_after=1.0)
            tw.type(lines[4])
            tw.type(lines[5], pause_after=0.5)
            tw.type(lines[6], pause_after=0.25)
            tw.type(lines[7], pause_after=0.25)
            tw.type(lines[8])
            tw.wait_for_continue()

        clear_screen()


def show_intro(player_name: str, sound_manager: SoundManager | None = None):
    intro = IntroStory(sound_manager=sound_manager)
    intro.show(player_name)
