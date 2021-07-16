from queue import Queue
from typing import Optional

from blessed import Terminal
from blessed.keyboard import Keystroke

from base import GameSection


class OverWorld(GameSection):
    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)
        # Any other needed initialization on game start here

    def handle_start(self, start_data: object):
        pass

    def run_processing(self,  inp: Optional[Keystroke]) -> bool:
        pass

    def run_rendering(self, terminal: Terminal):
        pass

    def handle_stop(self) -> object:
        pass
