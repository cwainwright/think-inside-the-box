import time
from enum import IntEnum
from functools import partial
from pathlib import Path
from queue import Queue
from random import choice
from string import ascii_uppercase
from typing import Optional

from blessed import Terminal
from blessed.keyboard import Keystroke
from pyfiglet import Figlet

from src.sections.base import GameSection
from src.util import question

# Constants
QUESTION_PATH = Path(__file__).parent / '..' / 'res/questions.json'
TYPING_SPEED = 50
echo = partial(print, end='', flush=True)

# A padding unit corresponds to 1/16th of the terminal width
get_padding_unit = lambda terminal: terminal.width // 16


class QuestionScreenState(IntEnum):
    INITIAL = 0
    WRITING_QUESTION = 1
    USER_SELECTION = 2
    REVEAL_ANSWER = 3


class Question(GameSection):
    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)
        self.questions_list = question.get_all_questions(QUESTION_PATH)
        self.state = QuestionScreenState.INITIAL

        # Initialize later
        self.question: question.Question = None
        self.start_y: int = None
        self.selected_index: int = None

    def handle_start(self, start_data: object):
        self.state = QuestionScreenState.INITIAL
        self.question = self._pick_question(start_data)
        self.selected_index = 0

    def run_processing(self,  inp: Optional[Keystroke]) -> bool:
        if self.state == QuestionScreenState.INITIAL:
            # Start writing the question to the screen
            self.state = QuestionScreenState.WRITING_QUESTION
            return True

        if inp == 'KEY_UP' and self.index > 0:
            self.index -= 1
            return True

        elif inp == 'KEY_DOWN' and self.index < (len(self.question.choices) - 1):
            self.index += 1
            return True

        elif inp == 'KEY_ENTER':
            self.state = QuestionScreenState.REVEAL_ANSWER
            return True

        return False

    def run_rendering(self, terminal: Terminal, _echo):
        if self.state == QuestionScreenState.WRITING_QUESTION:
            return self._write_question(terminal)

        self._redraw(terminal)

    def handle_stop(self) -> object:
        pass

    # Member Functions
    def _write_question(self, terminal):
        padding_unit = get_padding_unit(terminal)
        self._draw_question_mark(terminal)

        # Write the question prompt
        echo(terminal.move_xy(padding_unit, terminal.height // 4))
        echo("●  ")
        for ch in self.question.prompt:
            echo(terminal.bold_red(ch))
            time.sleep(1 / TYPING_SPEED)

        # Write the choices
        time.sleep(1)
        echo(terminal.move_down(2))
        self.start_y = terminal.get_location()[0]  # Remember at which Y location we start writing

        for i, choice in enumerate(self.question.choices):
            echo(terminal.move_x(padding_unit * 2) + terminal.move_down(1))
            echo((
                f"{terminal.bold_cyan}{ascii_uppercase[i]}."
                f" {terminal.normal + terminal.lawngreen}{choice}"
            ))
            time.sleep(0.5)

        self.state = QuestionScreenState.USER_SELECTION
        self._redraw(terminal)

    def _draw_question_mark(self, terminal):
        figlet = Figlet(font='doh', justify='right', width=terminal.width)
        render = figlet.renderText("?")
        cleaned = "\n".join(line for line in render.split("\n") if not line.isspace())
        padding = (terminal.height - cleaned.count("\n")) // 2
        echo(
            terminal.home
            + terminal.snow4
            + "\n" * padding
            + cleaned
            + terminal.normal
        )

    def _pick_question(self, data):
        # We don't have any special logic here yet
        return choice(self.questions_list)

    def _redraw(self, terminal):
        # Redraw the questions (A different one might be selected)
        echo(terminal.move_y(self.start_y))
        padding_unit = get_padding_unit(terminal)

        for i, choice in enumerate(self.question.choices):
            selected = self.selected_index == i
            echo(terminal.move_x(padding_unit * 2) + terminal.move_down(1))
            echo((
                f"{terminal.reverse if selected else ''}"
                f"{terminal.bold_cyan}{ascii_uppercase[i]}."
                f" {(terminal.normal + terminal.lawngreen) if self.state == QuestionScreenState.USER_SELECTION else ''}"
                f"{choice}{terminal.normal}"
            ))
