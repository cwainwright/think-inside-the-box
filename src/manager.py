import queue

from blessed import Terminal

from commands import StartGame, ChangeSection, EndGame
from sections.base import GameSection
from sections.over_world import OverWorld
from sections.menu import Menu
from sections.question import Question


class GameManager:
    def __init__(self, in_queue: queue.Queue, terminal: Terminal):
        self.terminal = terminal
        self.over_world: GameSection = OverWorld(in_queue)
        self.question: GameSection = Question(in_queue)
        self.menu: GameSection = Menu(in_queue)

    def __call__(self):
        active = self.menu
        data = StartGame()

        while not isinstance(data, EndGame):
            data = active(self.terminal, data)

            if isinstance(data, ChangeSection):
                active = getattr(self, data.new_section)
                data = data.data
