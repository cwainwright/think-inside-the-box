from queue import Queue
from typing import Callable, Optional

from blessed import Terminal
from blessed.keyboard import Keystroke

from src.commands import EndGame
from src.sections.base import GameSection


class GameOver(GameSection):
    """Class for Menu System"""

    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)

    def handle_start(self, start_data: object) -> bool:
        """Handles the screen start behaviour"""
        self.success_message_list = [
            " _______           _______  _______  _______  _______  _______  _",
            "(  ____ \\|\\     /|(  ____ \\(  ____ \\(  ____ \\(  ____ \\(  ____ \\( )",
            "| (    \\/| )   ( || (    \\/| (    \\/| (    \\/| (    \\/| (    \\/| |",
            "| (_____ | |   | || |      | |      | (__    | (_____ | (_____ | |",
            "(_____  )| |   | || |      | |      |  __)   (_____  )(_____  )| |",
            "      ) || |   | || |      | |      | (            ) |      ) |(_)",
            "/\\____) || (___) || (____/\\| (____/\\| (____/\\/\\____) |/\\____) | _",
            "\\_______)(_______)(_______/(_______/(_______/\\_______)\\_______)(_)"
        ]
        return True

    def run_processing(self, input: Optional[Keystroke]) -> bool:
        """Runs the screen input"""
        if input is not None:
            self.stop()
        return False

    def run_rendering(self, term: Terminal, echo: Callable[[str], None]) -> None:
        """Runs the screen rendering"""
        background_colour = term.black_on_skyblue

        # add the background colour and title
        echo(f"{term.home}{background_colour}{term.clear}")
        echo(term.center(term.darkblue_underline("Press any key to exit.")).rstrip())

        # get the whitespace to center text from the biggest line
        max_line: str = max(self.success_message_list)
        center_whitespace = ((term.width - len(max_line)) // 2) * " "

        # take the len of the list into account for y positioning
        center_y = (term.height - len(self.success_message_list)) // 2
        echo(term.move_y(center_y) + "\n")
        for line in self.success_message_list:
            echo(background_colour + center_whitespace + term.darkgreen(line).rstrip() + "\n")

        echo(term.normal)

    def handle_stop(self) -> object:
        """Handles the screen on stop which returns the endgame"""
        return EndGame()
