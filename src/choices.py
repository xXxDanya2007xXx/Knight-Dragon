#!/usr/bin/env python3

import readchar
from rich.console import Console, Group
from rich.live import Live
from rich.text import Text

from .sound_manager import SoundManager

NBSP = "\u00A0"


class ChoiceItem:
    def __init__(self, text: str):
        self.text: str = text

    def render(self, is_selected: bool) -> Text:
        prefix = Text(
            "---> ", style="bright_white") if is_selected else Text(NBSP * 5)
        text = Text(self.text, style="bright_white") if is_selected else Text(
            self.text)

        return prefix + text


class ChoicePrompt:
    console: Console

    def __init__(
            self,
            items: list[str],
            sound_manager: SoundManager | None = None
    ):
        self.items: list[ChoiceItem] = [ChoiceItem(i) for i in items]
        self.current_index: int = 0
        self.console = Console()
        self.sound: SoundManager | None = sound_manager

    def move_up(self):
        self.current_index = (self.current_index - 1) % len(self.items)
        if self.sound:
            self.sound.play("move")

    def move_down(self):
        self.current_index = (self.current_index + 1) % len(self.items)
        if self.sound:
            self.sound.play("move")

    def _render_view(self) -> Group:
        lines = [
            item.render(i == self.current_index)
            for i, item in enumerate(self.items)
        ]
        return Group(*lines)

    def ask(self) -> int:
        with Live(
            self._render_view(),
            console=self.console,
            refresh_per_second=30,
            screen=False,
        ) as live:
            while True:
                key = readchar.readkey()

                if key in ("k", readchar.key.UP):
                    self.move_up()
                elif key in ("j", readchar.key.DOWN):
                    self.move_down()
                elif key in ("l", readchar.key.ENTER):
                    if self.sound:
                        self.sound.play("select")
                    return self.current_index

                live.update(self._render_view())
