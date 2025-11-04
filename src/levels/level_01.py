#!/usr/bin/env python3

from rich.console import Console
from rich.text import Text

from ..choices import ChoicePrompt
from ..endings import show_game_over, show_victory
from ..sound_manager import SoundManager
from ..typewriter import Typewriter
from ..utils import clear_screen


class LevelOneStory:
    def __init__(self, sound_manager: SoundManager | None = None):
        self.sound_manager: SoundManager | None = sound_manager
        self.console: Console = Console()

    def show(self, player_name: str):
        clear_screen()

        lines = [
            "Some text...",
            "I don't really care 'bout it...",
            "",
            "Yet another text...",
        ]
        with Typewriter(
            lines_for_layout=lines,
            sound_manager=self.sound_manager,
            wait_for_input=False,
            show_footer=False,
        ) as tw:
            for line in lines:
                tw.type(line)

        self.console.print(Text())

        options = [
            "Very good option!",
            "Very bad option.",
        ]
        prompt = ChoicePrompt(options, sound_manager=self.sound_manager)
        selected = prompt.ask()

        if selected == 0:
            show_game_over(
                "That must be embarrasing...",
                sound_manager=self.sound_manager
            )
        else:
            show_victory(player_name, sound_manager=self.sound_manager)


def show_level_one(
        player_name: str,
        sound_manager: SoundManager | None = None
):
    level = LevelOneStory(sound_manager=sound_manager)
    level.show(player_name)
