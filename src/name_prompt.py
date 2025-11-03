#!/usr/bin/env python3

import threading
import time
from dataclasses import dataclass

import readchar
from rich.align import Align
from rich.box import ASCII
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from .sound_manager import SoundManager
from .utils import clear_screen

NBSP = "\u00A0"


class NamePrompt:
    @dataclass
    class State:
        name: str = ""
        mode: str = "input"
        cursor_visible: bool = True
        confirm_selected: int = 0

    def __init__(self, sound_manager: SoundManager | None = None):
        self.console: Console = Console()
        self.sound: SoundManager | None = sound_manager
        self.last_beep: float = 0.0
        self.beep_cooldown: float = 0.05

    def ask(self, field_width: int = 25) -> str:
        clear_screen()

        state = self.State()
        blink_interval = 0.5
        lock = threading.Lock()
        stop_blink = threading.Event()

        with Live(
            self._render_view(state, field_width),
            console=self.console,
            refresh_per_second=30,
            screen=True,
        ) as live:
            blink_thread = threading.Thread(
                target=self._blinker,
                args=(state, live, lock, stop_blink,
                      field_width, blink_interval),
                daemon=True,
            )
            blink_thread.start()

            done = False
            while not done:
                key = readchar.readkey()
                with lock:
                    if state.mode == "input":
                        done = self._handle_input_key(state, key, field_width)
                    else:
                        done = self._handle_confirm_key(state, key)
                live.update(self._render_view(state, field_width))

            stop_blink.set()
            blink_thread.join(timeout=0.1)

        return state.name

    def _play(self, sound_id: str):
        if self.sound:
            self.sound.play(sound_id)

    def _beep(self):
        now = time.time()
        if now - self.last_beep >= self.beep_cooldown:
            self.last_beep = now
            self._play("TXT1")

    def _render_view(self, state: "State", field_width: int):
        if state.mode == "input":
            return Align.center(
                self._render_input_panel(
                    state.name, state.cursor_visible, field_width)
            )
        return Align.center(
            self._render_confirm_panel(state.name, state.confirm_selected)
        )

    def _render_input_panel(
            self,
            name: str,
            cursor_visible: bool,
            field_width: int
    ) -> Panel:
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

    def _render_confirm_panel(self, name: str, selected: int) -> Panel:
        content = Group(
            Align.center(Text("Your name:", style="bright_white")),
            Align.center(Text(name if name else "—", style="bright_magenta")),
            Text(),
            Align.center(self._build_confirm_buttons(selected)),
        )
        return Panel(
            Align.center(content),
            title=Text("Confirm it!", style="bright_green"),
            box=ASCII,
            border_style="green",
            padding=(1, 5),
            expand=False,
        )

    def _build_input_line(
            self,
            name: str,
            cursor_visible: bool,
            field_width: int
    ) -> Text:
        placeholder = "Enter your name..."
        line = Text()

        if name:
            base = name[:field_width]
            _ = line.append(base, style="bright_magenta")
            _ = line.append(
                "█" if cursor_visible else NBSP,
                style="bright_white" if cursor_visible else "",
            )
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

    def _build_confirm_buttons(self, selected: int) -> Text:
        yes_style = "bold bright_green" if selected == 0 else "green"
        no_style = "bold bright_red" if selected == 1 else "red"

        btns = Text()
        _ = btns.append(" Yeah! ", style=yes_style)
        _ = btns.append(NBSP * 5)
        _ = btns.append(" No. ", style=no_style)
        return btns

    def _handle_input_key(
            self,
            state: "State",
            key: str,
            field_width: int
    ) -> bool:
        if key == readchar.key.ENTER:
            if state.name:
                state.mode = "confirm"
                state.confirm_selected = 0
                self._play("TXT2")
            return False

        if key == readchar.key.BACKSPACE:
            if state.name:
                state.name = state.name[:-1]
                self._beep()
            return False

        if key and key.isprintable() and len(state.name) < field_width:
            state.name += key
            self._beep()
        return False

    def _handle_confirm_key(self, state: "State", key: str) -> bool:
        if key in (readchar.key.LEFT, "h", "H"):
            if state.confirm_selected != 0:
                state.confirm_selected = 0
                self._beep()
            return False

        if key in (readchar.key.RIGHT, "l", "L"):
            if state.confirm_selected != 1:
                state.confirm_selected = 1
                self._beep()
            return False

        if key == readchar.key.ENTER:
            if state.confirm_selected == 0:
                self._play("TXT2")
                return True
            state.mode = "input"
            state.cursor_visible = True
            self._beep()
            return False

        k = key.lower()
        if k in ("y", "д"):
            self._play("TXT2")
            return True

        if k in ("n", "н", "q"):
            state.mode = "input"
            state.cursor_visible = True
            self._beep()
        return False

    def _blinker(
        self,
        state: "State",
        live: Live,
        lock: threading.Lock,
        stop: threading.Event,
        field_width: int,
        blink_interval: float,
    ):
        while not stop.is_set():
            time.sleep(blink_interval)
            with lock:
                if state.mode == "input":
                    state.cursor_visible = not state.cursor_visible
                live.update(self._render_view(state, field_width))
