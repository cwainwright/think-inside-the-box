from queue import Queue
from typing import Callable, Optional

from blessed import Terminal
from blessed.keyboard import Keystroke

from src.commands import ChangeSection, StartGame
from src.sections.base import GameSection
from src.sections.menu import StartMenuType


class Bootstrap(GameSection):
    """Initial component of the game, used as startup"""

    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)

    def handle_start(self, start_data: object) -> bool:
        """Inherit"""
        if not isinstance(start_data, StartGame):
            raise TypeError('Bootstrap only handles starting a game')
        return False

    def run_processing(self, inp: Optional[Keystroke]) -> bool:
        """Inherit"""
        self.stop()
        return False

    def run_rendering(self, terminal: Terminal, echo: Callable[[str], None]) -> None:
        """Inherit"""
        raise NotImplementedError('Bootstrap should not be used to render anything')

    def handle_stop(self) -> object:
        """Inherit"""
        return ChangeSection('menu', StartMenuType())
