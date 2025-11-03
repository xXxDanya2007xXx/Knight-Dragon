#!/usr/bin/env python3

import readchar
from rich.align import Align
from rich.box import ASCII
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from .name_prompt import NamePrompt
from .sound_manager import SoundManager
from .levels.intro import show_intro
from .utils import clear_screen, show_placeholder

NBSP = "\u00A0"


class InputHandler:
    def __init__(self):
        pass

    def get_action(self) -> str:
        key = readchar.readkey()

        if key in ("k", readchar.key.UP):
            return "up"
        if key in ("j", readchar.key.DOWN):
            return "down"
        if key in ("l", readchar.key.ENTER):
            return "select"
        if key.lower() == "q":
            return "quit"
        return "none"


class MenuItem:
    def __init__(self, text: str, enabled: bool = True, is_exit: bool = False):
        self.text: str = text
        self.enabled: bool = enabled
        self.is_exit: bool = is_exit

    def render(self, is_selected: bool) -> Text:
        if is_selected:
            prefix = Text("---> ", style="bright_white")
            rprefix = Text(" <---", style="bright_white")
            style = "bright_white" if self.enabled else "bright_black"
        else:
            prefix = Text(NBSP * 5 + "\u200B")
            rprefix = Text(NBSP * 5 + "\u200B")
            style = "white" if self.enabled else "bright_black"

        return prefix + Text(self.text, style=style) + rprefix


class Display:
    console: Console

    def __init__(self):
        self.console = Console()

    def show_ascii_art(self, filename: str, color: str = "bright_magenta"):
        try:
            with open(filename, encoding="utf-8") as file:
                art = file.read()
            self.console.print(Align.center(f"[{color}]{art}[/{color}]"))
        except FileNotFoundError:
            self.console.print(
                Text(f"File {filename} not found!"),
                style="bright_red",
                justify="center",
            )

    def show_help_text(self):
        self.console.print()
        help_text = (
            "Use [bright_white]↑ ↓[/bright_white] to navigate, "
            "[bright_white]Enter[/bright_white] to select, "
            "[bright_red]q[/bright_red] - quit the game"
        )
        self.console.print(help_text, justify="center")


class Menu:
    def __init__(
            self,
            items: list[MenuItem],
            sound_manager: SoundManager | None = None
    ):
        self.items: list[MenuItem] = items
        self.current_index: int = 0
        self.display: Display = Display()
        self.sound: SoundManager | None = sound_manager

    def move_up(self):
        steps = 0
        while steps < len(self.items):
            self.current_index = (self.current_index - 1) % len(self.items)
            if self.items[self.current_index].enabled:
                if self.sound:
                    self.sound.play("move")
                break
            steps += 1

    def move_down(self):
        steps = 0
        while steps < len(self.items):
            self.current_index = (self.current_index + 1) % len(self.items)
            if self.items[self.current_index].enabled:
                if self.sound:
                    self.sound.play("move")
                break
            steps += 1

    def get_selected_item(self) -> MenuItem:
        return self.items[self.current_index]

    def render(self):
        menu_items = [
            Align.center(item.render(i == self.current_index))
            for i, item in enumerate(self.items)
        ]

        content = Group(*menu_items)
        menu_panel = Panel(
            Align.center(content),
            title=Text("Knight and& Dragon", style="bright_white"),
            box=ASCII,
            border_style="bright_black",
            padding=(1, 5),
            expand=False,
        )
        self.display.console.print(Align.center(menu_panel))

    def show(self, logo_path: str):
        clear_screen()
        if logo_path:
            self.display.show_ascii_art(logo_path)
        self.render()
        self.display.show_help_text()

    def handle_action(self, action: str) -> bool:
        if action == "up":
            self.move_up()
        elif action == "down":
            self.move_down()
        elif action == "select":
            if self.sound:
                self.sound.play("select")
            selected = self.get_selected_item()

            if selected.is_exit:
                return False

            if selected.text == "NEW GAME":
                prompt = NamePrompt(sound_manager=self.sound)
                player_name = prompt.ask()

                if player_name:
                    show_intro(player_name, sound_manager=self.sound)
            else:
                show_placeholder()
        elif action == "quit":
            return False

        return True


def main():
    sound = SoundManager(enabled=True)
    sound.load("move", "src/sounds/undertale-move-selection.wav")
    sound.load("select", "src/sounds/undertale-select.wav")
    sound.load("TXT1", "src/sounds/undertale-txt1.wav")
    sound.load("TXT2", "src/sounds/undertale-txt2.wav")
    sound.load("txtal", "src/sounds/undertale-txtal.wav")
    sound.play_music("src/sounds/undertale-start-menu.wav")

    items = [
        MenuItem("NEW GAME"),
        MenuItem("CONTINUE", enabled=False),
        MenuItem("EXIT", is_exit=True),
    ]
    menu = Menu(items, sound_manager=sound)
    input_handler = InputHandler()

    is_running = True
    while is_running:
        menu.show("src/logo.ascii")
        action = input_handler.get_action()
        is_running = menu.handle_action(action)

    clear_screen()


if __name__ == "__main__":
    main()
