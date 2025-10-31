#!/usr/bin/env python3

import pygame.mixer


class SoundManager:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

        if self.enabled:
            pygame.mixer.init()
            self.sounds = {}

    def load(self, name: str, filename: str):
        if not self.enabled:
            return

        try:
            self.sounds[name] = pygame.mixer.Sound(filename)
        except Exception:
            pass

    def play(self, name: str, volume: float = 1.0):
        if self.enabled and name in self.sounds:
            self.sounds[name].set_volume(volume)
            self.sounds[name].play()

    def play_music(self, filename: str, volume: float = 0.5, loop: bool = True):
        if not self.enabled:
            return

        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception:
            pass

    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()

    def set_music_volume(self, volume: float):
        if self.enabled:
            pygame.mixer.music.set_volume(volume)
