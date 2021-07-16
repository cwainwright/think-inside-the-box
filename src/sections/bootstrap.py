from queue import Queue
from typing import Callable, Optional

from blessed import Terminal
from blessed.keyboard import Keystroke

from src.commands import ChangeSection, StartGame
from src.sections.base import GameSection
from src.sections.menu import StartMenuType


class Bootstrap(GameSection):
    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)

    def handle_start(self, start_data: object):
        if not isinstance(start_data, StartGame):
            raise TypeError('Bootstrap only handles starting a game')

    def run_processing(self, inp: Optional[Keystroke]) -> bool:
        self.stop()
        return False

    def run_rendering(self, terminal: Terminal, echo: Callable[[str], None]):
        raise NotImplemented('Bootstrap should not be used to render anything')

    def handle_stop(self) -> object:
        return ChangeSection('menu', StartMenuType())
