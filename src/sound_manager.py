#!/usr/bin/env python3

import pygame.mixer


class SoundManager:
    enabled: bool
    sounds: dict[str, pygame.mixer.Sound]

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

        pygame.mixer.init()
        self.sounds = {}

    def load(self, name: str, filename: str) -> None:
        if not self.enabled:
            return

        self.sounds[name] = pygame.mixer.Sound(filename)

    def play(self, name: str, volume: float = 1.0) -> None:
        if self.enabled and name in self.sounds:
            self.sounds[name].set_volume(volume)
            _ = self.sounds[name].play()

    def play_music(
            self, filename: str, volume: float = 0.25, loop: bool = True
    ) -> None:
        if not self.enabled:
            return

        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self) -> None:
        if self.enabled:
            pygame.mixer.music.stop()

    def set_music_volume(self, volume: float) -> None:
        if self.enabled:
            pygame.mixer.music.set_volume(volume)
