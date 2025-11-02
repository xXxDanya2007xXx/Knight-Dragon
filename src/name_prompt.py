#!/usr/bin/env python3

import threading
import time
import readchar
from rich.align import Align
from rich.box import ASCII
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.live import Live

from .sound_manager import SoundManager
from .utils import clear_screen

NBSP = "\u00A0"


class NamePrompt:
    console: Console
    sound: SoundManager | None

    def __init__(self, sound_manager: SoundManager | None = None):
        self.console = Console()
        self.sound = sound_manager

    def _build_input_line(
            self,
            name: str,
            cursor_visible: bool,
            field_width: int) -> Text:
        placeholder = "Enter your name..."
        line = Text()

        if name:
            base = name[:field_width]
            _ = line.append(base, style="bright_magenta")

            _ = line.append(
                "█" if cursor_visible else NBSP,
                style="bright_white" if cursor_visible else "")

            pad_len = max(0, field_width - len(base))
            if pad_len:
                _ = line.append(NBSP * pad_len)
        else:
            base = placeholder[:field_width]
            for i, ch in enumerate(base):
                if cursor_visible and i == 0:
                    _ = line.append(ch, style="black on bright_white")
                else:
                    _ = line.append(ch, style="bright_black")

            if len(base) < field_width:
                _ = line.append(NBSP * (field_width - len(base)))

            _ = line.append(NBSP)

        return line

    def _render_input_panel(
            self,
            name: str,
            cursor_visible: bool,
            field_width: int = 25) -> Panel:
        input_line = self._build_input_line(name, cursor_visible, field_width)
        content = Group(Align.center(input_line))
        return Panel(
            Align.center(content),
            title=Text("Name yourself.", style="bright_white"),
            box=ASCII,
            border_style="bright_black",
            padding=(1, 5),
            expand=False,
        )

    def _render_confirm_buttons(self, selected: int) -> Text:
        yes_style = "bold bright_green" if selected == 0 else "green"
        no_style = "bold bright_red" if selected == 1 else "red"

        btns = Text()
        _ = btns.append(" Yeah! ", style=yes_style)
        _ = btns.append(NBSP * 5)
        _ = btns.append(" No. ", style=no_style)
        return btns

    def _render_confirm_panel(self, name: str, selected: int) -> Panel:
        content = Group(
            Align.center(Text("Your name:", style="bright_white")),
            Align.center(Text(name if name else "—", style="bright_magenta")),
            Text(),
            Align.center(self._render_confirm_buttons(selected)),
        )
        return Panel(
            Align.center(content),
            title=Text("Confirm it!", style="bright_green"),
            box=ASCII,
            border_style="green",
            padding=(1, 5),
            expand=False,
        )

    def ask(self, field_width: int = 25) -> str:
        clear_screen()

        name = ""
        cursor_visible = True
        blink_interval = 0.5

        mode = "input"
        confirm_selected = 0

        lock = threading.Lock()
        stop_blink = threading.Event()

        def render():
            with lock:
                if mode == "input":
                    return Align.center(
                        self._render_input_panel(
                            name, cursor_visible, field_width))
                else:
                    return Align.center(
                        self._render_confirm_panel(
                            name, confirm_selected))

        def blinker(live_obj: Live):
            nonlocal cursor_visible
            while not stop_blink.is_set():
                time.sleep(blink_interval)
                with lock:
                    if mode == "input":
                        cursor_visible = not cursor_visible
                live_obj.update(render())

        with Live(
            render(),
            console=self.console,
            refresh_per_second=30,
            screen=True
        ) as live:
            blink_thread = threading.Thread(
                target=blinker, args=(live,), daemon=True)
            blink_thread.start()

            while True:
                key = readchar.readkey()

                with lock:
                    if mode == "input":
                        if key == readchar.key.ENTER:
                            mode = "confirm"
                            confirm_selected = 0
                            if not name:
                                mode = "input"
                            if self.sound:
                                self.sound.play("TXT2")
                        elif key == readchar.key.BACKSPACE:
                            if name:
                                name = name[:-1]
                                if self.sound:
                                    self.sound.play("TXT1")
                        elif key and key.isprintable() and len(name) < field_width:
                            name += key
                            if self.sound:
                                self.sound.play("TXT1")

                    else:
                        if key in (readchar.key.LEFT, "h", "H"):
                            if confirm_selected != 0:
                                confirm_selected = 0
                                if self.sound:
                                    self.sound.play("TXT1")
                        elif key in (readchar.key.RIGHT, "l", "L"):
                            if confirm_selected != 1:
                                confirm_selected = 1
                                if self.sound:
                                    self.sound.play("TXT1")
                        elif key == readchar.key.ENTER:
                            if confirm_selected == 0:
                                if self.sound:
                                    self.sound.play("TXT2")
                                stop_blink.set()
                                break
                            else:
                                mode = "input"
                                cursor_visible = True
                        elif key.lower() in ("y", "д"):
                            if self.sound:
                                self.sound.play("TXT2")
                            stop_blink.set()
                            break
                        elif key.lower() in ("n", "н", "q"):
                            mode = "input"
                            cursor_visible = True
                            if self.sound:
                                self.sound.play("TXT1")

                live.update(render())

            stop_blink.set()
            try:
                blink_thread.join(timeout=0.05)
            except Exception:
                pass

        return name
