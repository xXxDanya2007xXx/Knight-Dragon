#!/usr/bin/env python3

from .sound_manager import SoundManager
from .ui import Menu, NamePrompt
from .utils import clear_screen, show_placeholder

from .levels import intro, level_01


class Game:
    def __init__(self, sound_enabled: bool = True):
        self.player_name: str | None = None
        self.sound_manager: SoundManager | None = SoundManager(
            enabled=sound_enabled)
        self.name_prompt = NamePrompt(sound_manager=self.sound_manager)

        menu_items = [
            ("NEW GAME", self.new_game),
            ("CONTINUE", self.continue_game),
            ("EXIT", self.exit_game)
        ]
        self.menu = Menu(items=menu_items, sound_manager=self.sound_manager)

    def load_sounds(self):
        sm = self.sound_manager
        if not sm:
            return

        sm.load("move", "src/sounds/undertale-move-selection.wav")
        sm.load("select", "src/sounds/undertale-select.wav")
        sm.load("text", "src/sounds/undertale-txtal.wav")
        sm.load("TXT1", "src/sounds/undertale-txt1.wav")
        sm.load("TXT2", "src/sounds/undertale-txt2.wav")
        sm.play_music("src/sounds/undertale-start-menu.wav")

    def run(self):
        self.load_sounds()
        self.menu.show(logo_path="src/logo.ascii")
        self.shutdown()

    def new_game(self):
        name = self.name_prompt.ask()
        if not name:
            clear_screen()
            return True

        self.player_name = name
        clear_screen()

        intro.run(player_name=self.player_name,
                  sound_manager=self.sound_manager)
        level_01.run(player_name=self.player_name,
                     sound_manager=self.sound_manager)

        clear_screen()
        return True

    def continue_game(self):
        show_placeholder()
        clear_screen()
        return True

    def exit_game(self):
        return False

    def shutdown(self):
        clear_screen()
        if self.sound_manager:
            self.sound_manager.stop_music()
        print("Thx for playin'")
