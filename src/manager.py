import queue

from blessed import Terminal

from src.commands import ChangeSection, EndGame, StartGame
from src.sections.bootstrap import Bootstrap
from src.sections.menu import Menu
from src.sections.over_world import OverWorld
from src.sections.question import Question


class GameManager:
    """Game manager class"""

    def __init__(self, in_queue: queue.Queue, terminal: Terminal):
        self.terminal = terminal
        self.over_world = OverWorld(in_queue)
        self.question = Question(in_queue)
        self.menu = Menu(in_queue)
        self.bootstrap = Bootstrap(in_queue)

    def __call__(self):
        """Call dunder method"""
        active = self.bootstrap
        data = StartGame()

        while not isinstance(data, EndGame):
            data = active(self.terminal, data)

            if isinstance(data, ChangeSection):
                active = getattr(self, data.new_section)
                data = data.data
