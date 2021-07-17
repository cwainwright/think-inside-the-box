from queue import Queue
from typing import Callable, Optional

from blessed import Terminal
from blessed.keyboard import Keystroke

from src.commands import ChangeSection, EndGame
from src.sections.base import GameSection


class Debug(GameSection):
    """A game section for debugging purposes"""

    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)
        self.start_data = None

    def handle_start(self, start_data: object) -> bool:
        """Inherit"""
        self.start_data = start_data
        return True

    def run_processing(self, inp: Optional[Keystroke]) -> bool:
        """Inherit"""
        if inp is not None:
            self.stop()
            return False

    def run_rendering(self, terminal: Terminal, echo: Callable[[str], None]) -> None:
        """Inherit"""
        echo(terminal.clear)
        echo(terminal.move_xy(0, 0))
        echo(self.start_data)
        if isinstance(self.start_data, ChangeSection):
            echo('\n')
            echo(self.start_data.data)
        echo('\n\n')
        echo('Press any key to end the game...')

    def handle_stop(self) -> object:
        """Inherit"""
        return EndGame()
