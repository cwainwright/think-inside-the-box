import queue
from abc import ABC, abstractmethod
from functools import partial
from typing import Callable, Optional

from blessed import Terminal
from blessed.keyboard import Keystroke

echo = partial(print, end='', flush=True)


class GameSection(ABC):
    """The abstraction of a section of the game to be run.

    This class has 4 abstract methods that need implementing:
        - handle_start which is called once each time this section of the game is started (e.g. passing from a question back to the over world)
        - run_processing which receives the player input and is called repeatedly (once per frame), this is where you will implement most of your logic
        - run_rendering which handles the rendering of the current state using Blessed, only called if run_processing returns True
        - handle_stop which is called once each time this section of the game is started, just before it stops and hands control back to the manager

    Useful methods provided:
        - stop() which should be called to indicate this game section should stop (e.g. you encounter an NPC on the over world)
    """

    def __init__(self, in_queue: queue.Queue):
        self._in_queue = in_queue
        self._running = True

    def __call__(self, terminal, start_data):
        if self.handle_start(start_data):
            self.run_rendering(terminal, echo)

        while self._running:
            inp = self._get_input()
            if self.run_processing(inp):
                self.run_rendering(terminal, echo)

        return self.handle_stop()

    def stop(self):
        """Call to cease the running of the game section after a potential final render"""
        self._running = False

    @abstractmethod
    def handle_start(self, start_data: object) -> bool:
        """Handle any start data passed when the game section is started"""
        pass

    @abstractmethod
    def run_processing(self, inp: Optional[Keystroke], first_loop: bool) -> bool:
        """Handle any processing for the game section

        The input is either None (for no user input this cycle), or the keystroke the user made.
        Keystrokes can be compared to strings, e.g. inp == 'a', and some may be longer strings like 'KEY_LEFT'.

        Return True to perform a rendering step, return false otherwise
        """
        pass

    @abstractmethod
    def run_rendering(self, terminal: Terminal, echo: Callable[[str], None]):
        """Handle the rendering of the current state of the game section to the terminal"""
        pass

    @abstractmethod
    def handle_stop(self) -> object:
        """Handle the game section being stopped

        This method should perform any wrap up operation needed and return the operation to perform by the manager.
        Currently the operations are instances of ChangeSection or EndGame.
        """
        pass

    def _get_input(self) -> Optional[str]:
        try:
            return self._in_queue.get_nowait()
        except queue.Empty:
            return None
