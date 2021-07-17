import time
from enum import IntEnum
from functools import partial
from pathlib import Path
from queue import Queue
from random import choice
from string import ascii_uppercase
from typing import Callable, Optional

from blessed import Terminal
from blessed.keyboard import Keystroke
from pyfiglet import Figlet

from src.sections.base import GameSection
from src.util import question

# Constants
QUESTION_PATH = Path(__file__).parent / '..' / 'res/questions.json'
TYPING_SPEED = 40
echo = partial(print, end='', flush=True)


def get_padding_unit(terminal: Terminal) -> int:
    """Gets a padding unit corresponding to 1/16th of the terminal width"""
    return terminal.width // 16


class QuestionScreenState(IntEnum):
    """The possible states the Question screen can be in"""

    INITIAL = 0
    WRITING_QUESTION = 1
    USER_SELECTION = 2
    REVEAL_ANSWER = 3


class Question(GameSection):
    """The question screen section of the game"""

    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)
        self.questions_list = question.get_all_questions(QUESTION_PATH)
        self.state = QuestionScreenState.INITIAL

        # Initialize later
        self.question: question.Question = None
        self.start_y: int = None
        self.selected_index: int = None
        self.return_value: bool = None

    def handle_start(self, start_data: object) -> bool:
        """Inherit"""
        self.state = QuestionScreenState.INITIAL
        self.question = self._pick_question(start_data)
        self.selected_index = 0

    def run_processing(self, inp: Optional[Keystroke]) -> bool:
        """Inherit"""
        if self.state == QuestionScreenState.INITIAL:
            # Start writing the question to the screen
            self.state = QuestionScreenState.WRITING_QUESTION
            return True

        if not inp:
            return False

        if inp.name == 'KEY_UP' and self.selected_index > 0:
            self.selected_index -= 1
            return True

        elif inp.name == 'KEY_DOWN' and self.selected_index < (len(self.question.choices) - 1):
            self.selected_index += 1
            return True

        elif inp.name == 'KEY_ENTER':
            self.state = QuestionScreenState.REVEAL_ANSWER
            return True

        return False

    def run_rendering(self, terminal: Terminal, _echo: Callable[[str], None]) -> None:
        """Inherit"""
        if self.state == QuestionScreenState.WRITING_QUESTION:
            return self._write_question(terminal)

        self._redraw(terminal)

        if self.state == QuestionScreenState.REVEAL_ANSWER:
            return self._write_answer(terminal)

    def handle_stop(self) -> object:
        """Inherit"""
        return self.return_value

    # Member Functions
    def _write_question(self, terminal: Terminal) -> None:
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
        # termnial.get_location() doesn't seem to be working in multithreaded,
        # so we assume the question is only 1 line long
        self.start_y = (terminal.height // 4) + 2

        for i, choice_ in enumerate(self.question.choices):
            echo(terminal.move_x(padding_unit * 2) + terminal.move_down(1))
            echo((
                f"{terminal.bold_cyan}{ascii_uppercase[i]}."
                f" {terminal.normal + terminal.lawngreen}{choice_}"
            ))
            time.sleep(0.75)

        self.state = QuestionScreenState.USER_SELECTION
        self._redraw(terminal)

    def _draw_question_mark(self, terminal: Terminal) -> None:
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

    def _write_answer(self, terminal: Terminal) -> None:
        correct = self.question.is_index_correct(self.selected_index)
        if correct:
            self._write_footer(terminal, terminal.white + "▶" + terminal.bold_green + "  CORRECT!!")
        else:
            self._write_footer(terminal, terminal.white + "▶" + terminal.bold_red + "  INCORRECT!!")

        time.sleep(3)
        self.return_value = correct
        echo(terminal.normal)
        self.stop()

    def _pick_question(self, data: object) -> question.Question:
        # if data is a string, pick a question that matches .startswith()
        if type(data) == str:
            return choice([q for q in self.questions_list if q.id.startswith(data)])

        # Otherwise, return a random non-special question
        return choice([q for q in self.questions_list if not q.id.startswith('special-')])

    def _redraw(self, terminal: Terminal) -> None:
        # Redraw the questions (A different one might be selected)
        echo(terminal.move_y(self.start_y))
        padding_unit = get_padding_unit(terminal)

        for i, choice_ in enumerate(self.question.choices):
            selected = self.selected_index == i
            echo(terminal.move_x(padding_unit * 2) + terminal.move_down(1))
            echo(f"{terminal.reverse if selected else ''}")
            echo(f"{terminal.bold_cyan}{ascii_uppercase[i]}.")

            in_selection_state_or_not_selected = self.state == QuestionScreenState.USER_SELECTION or not selected
            echo(f" {(terminal.normal + terminal.lawngreen) if in_selection_state_or_not_selected else ''}")

            echo(f"{choice_}{terminal.normal}")

    def _write_footer(self, terminal: Terminal, text: str) -> None:
        padding_unit = get_padding_unit(terminal)
        echo(
            terminal.move_xy(padding_unit, self.start_y)
            + terminal.move_down(len(self.question.choices) + 3)
            + text
        )
