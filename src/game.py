import threading
from queue import Queue

from blessed import Terminal

FPS = 60


class Game:
    """The top level class for the game"""

    def __init__(self, manager_cls: type):
        self.manager_cls = manager_cls

    def run(self) -> None:
        """The run method for the game, handling the TUI"""
        term = Terminal()
        input_queue = Queue()

        manager = self.manager_cls(input_queue, term)
        manager_thread = threading.Thread(target=manager)
        manager_thread.start()

        with term.fullscreen(), term.raw(), term.hidden_cursor(), term.location():
            while manager_thread.is_alive():
                inp = term.inkey(1 / FPS)

                if inp != '':
                    input_queue.put(inp)

            print(term.normal + term.clear)
