from queue import Queue
from typing import Callable, Optional

from blessed import Terminal
from blessed.keyboard import Keystroke

from src.sections.base import GameSection


class OverWorld(GameSection):
    """Over world game section"""

    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)
        # Any other needed initialization on game start here

    def handle_start(self, start_data: object) -> bool:
        """Inherit"""
        pass

    def run_processing(self, inp: Optional[Keystroke]) -> bool:
        """Inherit"""
        pass

    def run_rendering(self, terminal: Terminal, echo: Callable[[str], None]) -> None:
        """Inherit"""
        pass

    def handle_stop(self) -> object:
        """Inherit"""
        pass
