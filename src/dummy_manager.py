import queue
from abc import ABC, abstractmethod

from blessed import Terminal

from src.sections.debug import Debug
from src.sections.menu import Menu, StartMenuType
from src.sections.over_world import OverWorld
from src.sections.question import NewQuestion, Question


class DummyGameManager(ABC):
    """A dummy game manager for testing purposes"""

    def __init__(self, in_queue: queue.Queue, terminal: Terminal):
        self.terminal = terminal
        self.in_queue = in_queue

    @property
    @abstractmethod
    def section_class(self) -> type:
        """The section class to test"""
        pass

    @property
    @abstractmethod
    def start_data(self) -> object:
        """The start data to provide to the section"""
        pass

    def __call__(self):
        """Run the dummy manager loop"""
        section = self.section_class(self.in_queue)
        data = section(self.terminal, self.start_data)
        debug = Debug(self.in_queue)
        debug(self.terminal, data)


class DummyMenuManager(DummyGameManager):
    """Dummy manager for the Menu"""

    section_class = Menu
    start_data = StartMenuType()


class DummyOverWorldManager(DummyGameManager):
    """Dummy manager for the over world"""

    section_class = OverWorld
    start_data = None


class DummyQuestionManager(DummyGameManager):
    """Dummy manager for the question screen"""

    section_class = Question
    start_data = NewQuestion()
