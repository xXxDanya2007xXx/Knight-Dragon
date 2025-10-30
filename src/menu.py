#!/usr/bin/env python3

from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
import readchar
import os


class InputHandler:
    def __init__(self):
        pass

    def get_action(self) -> str:
        key = readchar.readkey()

        if key == readchar.key.UP:
            return "up"
        elif key == readchar.key.DOWN:
            return "down"
        elif key == readchar.key.ENTER:
            return "select"
        elif key.lower() == "q":
            return "quit"
        else:
            return "none"


class MenuItem:
    def __init__(self, text: str, enabled: bool = True):
        self.text = text
        self.enabled = enabled

    def render(self, is_selected: bool) -> Text:
        prefix = "> " if is_selected else "  "

        if is_selected:
            if self.enabled:
                style = "bold white"
            else:
                style = "bold black"
        else:
            if self.enabled:
                style = "white"
            else:
                style = "bold black"

        if not self.enabled and is_selected:
            return Text("> ", style="bold white") + Text(self.text, style=style)
        else:
            return Text(f"{prefix}{self.text}", style=style)


class Display:
    def __init__(self):
        self.console = Console()

    def clear_screen(self):
        _ = os.system("cls" if os.name == "nt" else "clear")

    def show_ascii_art(self, filename: str, color: str = "bold magenta"):
        try:
            with open(filename, encoding="utf-8") as file:
                art = file.read()
            self.console.print(Align.center(f"[{color}]{art}[/{color}]"))
        except FileNotFoundError:
            self.console.print(f"[bold red]File {
                               filename} not found![/bold red]", justify="center")

    def show_help_text(self):
        self.console.print()
        self.console.print("Используйте [bold white]↑ ↓[/bold white] для навигации, ",
                           "[bold white]Enter[/bold white] для выбора, ",
                           "[bold red]q[/bold red] - завершить игру",
                           justify="center")


class Menu:
    def __init__(self, items: list[MenuItem]):
        self.items = items
        self.current_index = 0
        self.display = Display()

    def move_up(self):
        steps = 0
        while steps < len(self.items):
            self.current_index = (self.current_index - 1) % len(self.items)
            if self.items[self.current_index].enabled:
                break
            steps += 1

    def move_down(self):
        steps = 0
        while steps < len(self.items):
            self.current_index = (self.current_index + 1) % len(self.items)
            if self.items[self.current_index].enabled:
                break
            steps += 1

    def get_selected_item(self) -> MenuItem:
        return self.items[self.current_index]

    def render(self):
        for i, item in enumerate(self.items):
            is_selected = (i == self.current_index)

            render_text = item.render(is_selected)

            self.display.console.print(render_text, justify="center")

    def show(self, logo_path: str):
        self.display.clear_screen()
        if logo_path:
            self.display.show_ascii_art(logo_path, color="bold magenta")

        self.render()

        self.display.show_help_text()

    def handle_action(self, action: str) -> bool:
        if action == "up":
            self.move_up()
            return True
        elif action == "down":
            self.move_down()
            return True
        elif action == "select":
            selected = self.get_selected_item()

            if selected.text == "EXIT":
                return False

            self.display.clear_screen()
            panel = Panel.fit(Text("Нажмите Enter, чтобы вернуться...",
                              style="bold white", justify="center"),
                              border_style="bold black")
            self.display.console.print(panel, justify="center")
            _ = input()
            return True
        elif action == "quit":
            return False
        else:
            return True


if __name__ == "__main__":
    items = [MenuItem("NEW GAME"), MenuItem(
        "CONTINUE", enabled=False), MenuItem("EXIT")]

    menu = Menu(items)
    input_handler = InputHandler()

    running = True
    while running:
        menu.show("src/logo.ascii")

        action = input_handler.get_action()

        running = menu.handle_action(action)

    menu.display.clear_screen()
