#!/usr/bin/env python3

from ..utils import clear_screen, show_placeholder
from ..ui import Typewriter, ChoicePrompt
from ..sound_manager import SoundManager
from .. import endings


def run(player_name: str, sound_manager: SoundManager | None = None):
    clear_screen()
    player_name = player_name if player_name else "Knight"

    lines = [
        "Перед тобой огромное озеро.",
        "Или море?",
        "",
        "В любом случае...",
        "",
        "Сейчас его перелетает злой дракон!",
        "Он похитил принцессу, и она очень громко визжит в его лапах.",
        "",
        "Несмотря на это, твой рыцарский долг - спасти ее.",
        "Ты должен догнать дракона, и для этого нужно переплыть озеро!",
    ]

    with Typewriter(lines_for_layout=lines, sound_manager=sound_manager) as tw:
        for line in lines:
            tw.type(line)

    choice_prompt = ChoicePrompt(
        options=[
            "Начать героически плыть!",
            "Позорно отступить и начать думать.",
        ],
        sound_manager=sound_manager
    )

    choice = choice_prompt.ask("Решай быстро - дракон продолжает улетать!")

    if choice == 0:
        endings.show_game_over(
            (
                "Ты утонул.",
                "Кажется, плавать в доспехах - не самая удачная идея.",
            ),
            sound_manager
        )
    else:
        # endings.show_victory(player_name, sound_manager)
        show_placeholder()
