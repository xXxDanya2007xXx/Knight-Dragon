#!/usr/bin/env python3

import os
import sys
import time
from types import TracebackType

import readchar
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.text import Text

from .sound_manager import SoundManager

NBSP = "\u00A0"


class Typewriter:
    def __init__(
        self,
        lines_for_layout: list[str],
        title: str = "",
        sound_manager: SoundManager | None = None,
        char_delay: float = 0.025,
        beep_every: int = 3,
        wait_for_input: bool = True,
        show_footer: bool = True,
    ):
        self.console: Console = Console()
        self.sound: SoundManager | None = sound_manager
        self.char_delay: float = char_delay
        self.beep_every: float = beep_every
        self.last_beep: float = 0.0
        self.beep_cooldown: float = 0.05

        self._title: str = title
        self._all_lines: list[str] = lines_for_layout
        self._typed_lines: list[Text] = []
        self._live: Live | None = None
        self._wait_for_input: bool = wait_for_input
        self._show_footer: bool = show_footer

        self._animating: bool = True
        self._skip: bool = False
        self._continued: bool = False
        self._orig_tty: object | None = None
        self._content_width: int = self._calc_content_width()

    def __enter__(self):
        self._enable_cbreak()
        self._live = Live(
            self._render_view(),
            console=self.console,
            refresh_per_second=60,
            screen=False,
        )
        _ = self._live.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None
    ) -> bool:
        try:
            if self._wait_for_input and not self._continued:
                self.wait_for_continue()
        finally:
            if self._live:
                self._live.__exit__(exc_type, exc_val, exc_tb)
            self._disable_cbreak()
        return False

    def type(self, text: str, pause_after: float = 0.25):
        if self._skip:
            full_text = self._from_markup(text)
            self._typed_lines.append(full_text)
            self._after_line_complete()
            if self._live:
                self._live.update(self._render_view())
            return

        full_text = self._from_markup(text)
        self._typed_lines.append(Text())
        idx = len(self._typed_lines) - 1
        visible = 0
        plain = full_text.plain

        for i, ch in enumerate(plain):
            if self._check_skip():
                self._typed_lines[idx] = full_text
                if self._live:
                    self._live.update(self._render_view())
                break

            self._typed_lines[idx] = full_text[: i + 1]
            if ch not in (" ", NBSP):
                if self.beep_every > 0 and (visible % self.beep_every == 0):
                    self._beep()
                visible += 1

            if self._live:
                self._live.update(self._render_view())
            self._sleep_with_skip(self.char_delay)

        if not self._skip:
            self.pause(pause_after)
        self._after_line_complete()

    def pause(self, duration: float):
        if duration <= 0 or self._skip:
            return
        end = time.time() + duration
        while time.time() < end and not self._skip:
            self._sleep_with_skip(min(0.02, end - time.time()))

    def wait_for_continue(self):
        self._animating = False
        if self._live:
            self._live.update(self._render_view())
        while True:
            key = readchar.readkey()
            if key in ("l", "L", readchar.key.ENTER):
                self._play("select")
                break
            if key.lower() == "q":
                break
        self._continued = True

    def _after_line_complete(self):
        if len(self._typed_lines) == len(self._all_lines):
            self._animating = False
            if self._live:
                self._live.update(self._render_view())

    def _sleep_with_skip(self, dt: float):
        if dt <= 0:
            return
        t0 = time.time()
        while time.time() - t0 < dt:
            if self._check_skip():
                break
            time.sleep(0.005)

    def _check_skip(self) -> bool:
        key = self._readkey_nowait()
        if key is None:
            return False
        self._skip = True
        self._play("select")
        self._drain_input()
        return True

    def _drain_input(self):
        if os.name == "nt":
            try:
                import msvcrt
                while msvcrt.kbhit():
                    _ = msvcrt.getwch()
            except Exception:
                pass
        else:
            try:
                import select
                while True:
                    r, _, _ = select.select([sys.stdin], [], [], 0)
                    if not r:
                        break
                    _ = sys.stdin.read(1)
            except Exception:
                pass

    def _readkey_nowait(self):
        if os.name == "nt":
            try:
                import msvcrt
                if msvcrt.kbhit():
                    return msvcrt.getwch()
                return None
            except Exception:
                return None
        else:
            try:
                import select
                r, _, _ = select.select([sys.stdin], [], [], 0)
                if r:
                    return sys.stdin.read(1)
                return None
            except Exception:
                return None

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

    def _from_markup(self, text: str) -> Text:
        return Text.from_markup(text, style="white")

    def _play(self, sound_id: str):
        if self.sound:
            self.sound.play(sound_id)

    def _beep(self):
        now = time.time()
        if now - self.last_beep >= self.beep_cooldown:
            self.last_beep = now
            self._play("txtal")

    def _calc_content_width(self) -> int:
        return 0

    def _pad_to_width(self, txt: Text) -> Text:
        return txt

    def _render_view(self) -> Align:
        items: list[Text] = []
        if self._title:
            items.append(self._pad_to_width(
                Text(self._title, style="bright_white")))
            items.append(self._pad_to_width(Text()))
        for line in self._typed_lines:
            items.append(self._pad_to_width(line.copy()))
        remain = len(self._all_lines) - len(self._typed_lines)
        for _ in range(max(0, remain)):
            items.append(self._pad_to_width(Text()))

        if self._show_footer:
            items.append(self._pad_to_width(Text()))
            footer = (
                self._build_continue_footer()
                if not self._animating
                else self._build_skip_footer()
            )
            items.append(self._pad_to_width(footer))

        return Align.left(Group(*items))

    def _build_skip_footer(self) -> Text:
        return Text.assemble(
            ("Press ", "bright_black"),
            ("any key", "white"),
            (" to skip...", "bright_black"),
        )

    def _build_continue_footer(self) -> Text:
        return Text.assemble(
            ("Press ", "bright_black"),
            ("Enter", "white"),
            (" to continue...", "bright_black"),
        )
