#!/usr/bin/env python3

import os
import sys
import time
import readchar

from rich.align import Align
from rich.box import ASCII
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from .sound_manager import SoundManager
from .utils import clear_screen

NBSP = "\u00A0"  # Неразрывный пробел


class Typewriter:
    def __init__(
            self,
            lines_for_layout: list[str],
            sound_manager: SoundManager | None = None,
            char_delay: float = 0.05,
    ):
        self.console: Console = Console()
        self.sound: SoundManager | None = sound_manager
        self.char_delay: float = char_delay

        self._all_lines: list[str] = lines_for_layout
        self._typed_lines: list[Text] = []
        self._live: Live | None = None
        self._skip: bool = False
        self._orig_tty = None

    def __enter__(self):
        self._enable_cbreak()
        self._live = Live(
            self._render_view(),
            console=self.console,
            refresh_per_second=60,
            screen=False
        )
        _ = self._live.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._live:
            self._live.__exit__(exc_type, exc_val, exc_tb)

        self._disable_cbreak()
        self._drain_input()

    def _enable_cbreak(self):
        if os.name == "nt":
            return
        try:
            import termios
            import tty
            fd = sys.stdin.fileno()
            self._orig_tty = termios.tcgetattr(fd)
            _ = tty.setcbreak(fd)
        except Exception:
            self._orig_tty = None

    def _disable_cbreak(self):
        if os.name == "nt" or not self._orig_tty:
            return
        try:
            import termios
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, self._orig_tty)
        except Exception:
            pass

    def type(self, text: str, pause_after: float = 0.5):
        if self._skip:
            self._typed_lines.append(Text.from_markup(text))
            self._update_view()
            return

        line_text = Text.from_markup(text)
        self._typed_lines.append(Text())
        current_line_index = len(self._typed_lines) - 1

        for i in range(len(line_text.plain)):
            if self._check_skip():
                self._skip = True
                if self.sound:
                    self.sound.play("select")
                self._typed_lines[current_line_index] = line_text
                self._update_view()
                break

            self._typed_lines[current_line_index] = line_text[:i+1]
            if line_text.plain[i] not in (" ", NBSP) and self.sound:
                self.sound.play("text")

            self._update_view()
            time.sleep(self.char_delay)

        if not self._skip:
            time.sleep(pause_after)

    def wait_for_continue(self):
        self._skip = False
        self._drain_input()

        self._update_view(footer_text="Нажмите Enter для продолжения...")

        while True:
            key = readchar.readkey()

            if key == readchar.key.ENTER:
                if self.sound:
                    self.sound.play("select")
                break

    def _update_view(self, footer_text: str | None = None):
        if self._live:
            self._live.update(self._render_view(footer_text), refresh=True)

    def _render_view(self, footer_text: str | None = None):
        lines = list(self._typed_lines)
        padding = [Text() for _ in range(len(self._all_lines) - len(lines))]
        all_lines_typed = len(lines) == len(self._all_lines)

        if not footer_text and not self._skip and not all_lines_typed:
            footer_text = "Нажмите любую клавишу, чтобы пропустить..."

        footer = None
        if footer_text:
            footer = Text.from_markup(footer_text, style="bright_black")

        items = [*lines, *padding]
        if footer:
            items.append(Text())
            items.append(footer)

        return Group(*items)

    def _check_skip(self):
        if os.name == "nt":
            import msvcrt
            if msvcrt.kbhit():
                try:
                    _ = msvcrt.getwch()
                except Exception:
                    _ = msvcrt.getch()
                self._skip = True
                return True
        else:
            import select
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r:
                try:
                    _ = sys.stdin.read(1)
                except Exception:
                    pass
                self._skip = True
                return True
            return False

    def _drain_input(self):
        try:
            if os.name == "nt":
                import msvcrt
                while msvcrt.kbhit():
                    _ = msvcrt.getch()
            else:
                import termios
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
        except (ImportError, OSError, AttributeError):
            pass


class ChoicePrompt:
    def __init__(
        self,
        options: list[str],
        sound_manager: SoundManager | None = None,
    ):
        self.options: list[str] = options
        self.sound: SoundManager | None = sound_manager
        self.console: Console = Console()
        self.current_index: int = 0
        self.center: bool = False
        self.separator: bool = True

    def ask(self, prompt_text: str = "Сделайте выбор:"):
        prompt = Text.from_markup(prompt_text)

        with Live(
                self._render(prompt),
                console=self.console,
                screen=False,
                auto_refresh=False
        ) as live:
            live.update(self._render(prompt), refresh=True)
            while True:
                key = readchar.readkey()

                if key in (readchar.key.UP, "k"):
                    self.current_index = (
                        self.current_index - 1) % len(self.options)
                    if self.sound:
                        self.sound.play("move")
                elif key in (readchar.key.DOWN, "j"):
                    self.current_index = (
                        self.current_index + 1) % len(self.options)
                    if self.sound:
                        self.sound.play("move")
                elif key == readchar.key.ENTER:
                    if self.sound:
                        self.sound.play("select")
                    return self.current_index

                live.update(self._render(prompt), refresh=True)

    def _render(self, prompt: Text):
        lines: list[Text] = []
        for i, option in enumerate(self.options):
            if i == self.current_index:
                lines.append(
                    Text.from_markup(f"---> {option}", style="bold"))
            else:
                lines.append(Text.from_markup(f"{NBSP * 5}{option}"))

        elements: list[Text] = []

        elements.append(Text())
        if self.separator:
            elements.append(Text("-----" * 5, style="bright_black"))
            elements.append(Text())
        elements.append(prompt)
        elements.append(Text())
        elements.extend(lines)

        block = Group(*elements)
        return Align.center(block) if self.center else block


class NamePrompt:
    def __init__(self, sound_manager: SoundManager | None = None):
        self.sound: SoundManager | None = sound_manager
        self.console: Console = Console()

    def ask(self, prompt_text: str = "Name yourself."):
        clear_screen()
        name = ""

        with Live(
            self._render_input(prompt_text, name),
            console=self.console,
            auto_refresh=False
        ) as live:
            while True:
                live.update(Align.center(
                    self._render_input(prompt_text, name)
                ), refresh=True)
                key = readchar.readkey()

                if key == readchar.key.ENTER:
                    if name:
                        if self.sound:
                            self.sound.play("TXT2")
                        confirmed = self._confirm_name(name)
                        if confirmed:
                            return name
                        else:
                            clear_screen()
                            continue
                    else:
                        continue

                elif key == readchar.key.BACKSPACE:
                    name = name[:-1]
                    if self.sound:
                        self.sound.play("TXT1")

                elif key.isprintable() and len(name) < 15:
                    name += key
                    name = name.strip()
                    if self.sound:
                        self.sound.play("TXT1")

    def _render_input(self, prompt_text: str, name: str):
        cursor = Text("█", style="blink white")
        display_name = Text(name, style="bright_magenta") + cursor

        return Align.center(
            Panel(
                display_name,
                title=Text(prompt_text, style="bright_white"),
                box=ASCII,
                border_style="bright_black",
                padding=(1, 5),
                expand=False
            )
        )

    def _confirm_name(self, name: str):
        clear_screen()

        prompt = ChoicePrompt(
            options=[
                "[green]Да[/green], это я!",
                "[red]Нет[/red], это не я."
            ], sound_manager=self.sound)
        prompt.center = True
        prompt.separator = False

        choice = prompt.ask(
            f"Твое имя [bright_magenta]{name}[/bright_magenta]?"
        )
        return choice == 0


class Menu:
    def __init__(
        self,
        items: list[tuple[str, callable]],
        sound_manager: SoundManager | None = None
    ):
        self.items: list[tuple[str, callable]] = items
        self.sound: SoundManager | None = sound_manager
        self.console: Console = Console()
        self.current_index: int = 0
        self._logo: Text | None = None

    def get_logo(self, logo_path: str):
        try:
            with open(logo_path, "r", encoding="utf-8") as f:
                return Text(f.read(), justify="center", style="bright_magenta")
        except FileNotFoundError:
            return Text(
                f"Логотип не найден: {logo_path}",
                justify="center",
                style="bright_red"
            )

    def show(self, logo_path: str):
        clear_screen()

        self._logo = self.get_logo(logo_path)

        with Live(
            self._render(),
            console=self.console,
            screen=True,
            auto_refresh=False
        ) as live:
            live.update(self._render())
            is_running = True
            while is_running:
                key = readchar.readkey()

                if key in (readchar.key.UP, "k"):
                    self.current_index = (
                        self.current_index - 1) % len(self.items)
                    if self.sound:
                        self.sound.play("move")
                elif key in (readchar.key.DOWN, "j"):
                    self.current_index = (
                        self.current_index + 1) % len(self.items)
                    if self.sound:
                        self.sound.play("move")
                elif key == readchar.key.ENTER:
                    if self.sound:
                        self.sound.play("select")

                    _, action = self.items[self.current_index]

                    result = action()
                    if result is False:
                        is_running = False
                    else:
                        clear_screen()
                elif key.lower() == "q":
                    is_running = False

                live.update(self._render(), refresh=True)

    def _render(self):
        lines = []
        for i, (text, _) in enumerate(self.items):
            is_exit = "EXIT" in text.upper()

            if i == self.current_index:
                style = "bright_red" if is_exit else "bright_white"
                lines.append(
                    Text(f"---> {text} <---", justify="center", style=style))
            else:
                style = "red" if is_exit else "white"
                lines.append(Text(text, justify="center", style=style))

        help_text = Text(
            "Use ↑ ↓ to navigate, Enter to select, q to quit",
            style="bright_black"
        )

        menu_panel = Panel(
            Group(*lines, Text(), help_text),
            title=Text("Knight and& Dragon", style="bright_white"),
            border_style="bright_black",
            box=ASCII,
            padding=(1, 5)
        )

        header = self._logo if self._logo else Text()
        return Align.center(Group(header, Text(), menu_panel))
