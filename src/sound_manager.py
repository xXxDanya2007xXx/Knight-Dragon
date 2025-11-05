#!/usr/bin/env python3

import pygame
import pygame.mixer


class SoundManager:
    def __init__(self, enabled: bool = True):
        self.enabled: bool = enabled
        if not self.enabled:
            return

        _ = pygame.init()
        pygame.mixer.init()

        self.sounds: dict[str, pygame.mixer.Sound] = {}

    def load(self, name: str, filename: str):
        if not self.enabled:
            return

        self.sounds[name] = pygame.mixer.Sound(filename)

    def play(self, name: str, volume: float = 0.5):
        if self.enabled and name in self.sounds:
            sound = self.sounds[name]
            sound.set_volume(volume)
            _ = sound.play()

    def play_music(
            self,
            filename: str,
            volume: float = 0.25,
            loop: bool = True
    ):
        if not self.enabled:
            return

        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()
