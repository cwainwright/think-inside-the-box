from dataclasses import dataclass
from queue import Queue
from typing import Callable, Optional

from blessed import Terminal
from blessed.keyboard import Keystroke

from src.commands import ChangeSection, EndGame
from src.sections.base import GameSection


class MenuType:
    """Menu Type super class"""

    pass


@dataclass
class StartMenuType(MenuType):
    """Start menu type sub class"""

    character: str = '🙂'


@dataclass
class CharacterMenuType(MenuType):
    """Character menu type sub class"""

    character: str


class StartMenuBehaviour:
    """Start Menu Bahaviour class"""

    title = 'Start Menu'
    menu_list = [
        'Play',
        'Character Select',
        'Quit',
    ]

    def initial_selection(self, _) -> int:  # noqa: ANN001
        """
        Returns the menu initial selection

        which is 0 by default on the main menu
        """
        return 0

    def is_valid_selection(self, index: int) -> bool:
        """Returns true if given selection index is valid"""
        return index in range(len(self.menu_list))

    def next_command(self, index: int, character: str) -> object:
        """Processes the next command after selection"""
        if index == 0:
            return ChangeSection('over_world', object())

        if index == 1:
            return ChangeSection('menu', CharacterMenuType(character))

        if index == 2:
            return EndGame()


class CharacterMenuBehaviour:
    """Character Menu Bahaviour class"""

    title = 'Character Select'
    menu_list = [
        '🙂',
        '😄',
        '😐',
        '🤔',
        '🙁',
        '😎',
        '🙃',
        '😂',
        '😭',
    ]

    def initial_selection(self, character: str) -> int:
        """Gets the menu initial selection"""
        return self.menu_list.index(character)

    def is_valid_selection(self, index: int) -> bool:
        """Returns true if given selection index is valid"""
        return index in range(len(self.menu_list))

    def next_command(self, index: int, _) -> ChangeSection:  # noqa: ANN001
        """
        Processes the next command after selection

        After character menu it returns to main menu
        """
        return ChangeSection('menu', StartMenuType(self.menu_list[index]))


class Menu(GameSection):
    """Class for Menu System"""

    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)
        self.character_emoji = "🙂"

    def handle_start(self, start_data: MenuType) -> bool:
        """Handles the menu start behaviour"""
        behaviour_class = {
            StartMenuType: StartMenuBehaviour,
            CharacterMenuType: CharacterMenuBehaviour,
        }[type(start_data)]
        self.behaviour = behaviour_class()

        try:
            self.character_emoji = start_data.character
        except AttributeError:
            pass

        self.selected = self.behaviour.initial_selection(self.character_emoji)

        return True

    def run_processing(self, input: Optional[Keystroke]) -> bool:
        """Runs the menu processing getting user input and choice"""
        if input is None:
            return False

        menu_list = self.behaviour.menu_list

        # save the choice by the number pressed
        try:
            new_selected = int(input) - 1
            if self.behaviour.is_valid_selection(new_selected):
                self.selected = new_selected
                self.stop()
                return False
        except (ValueError):
            pass

        # save the choice by currently selected item on enter key press
        if input.name == "KEY_ENTER":
            self.stop()
            return False

        # move selection up
        if input.name == "KEY_UP" or input == "w":
            self.selected = (self.selected - 1) % len(menu_list)
            return True

        # move selection down
        if input.name == "KEY_DOWN" or input == "s":
            self.selected = (self.selected + 1) % len(menu_list)
            return True

        return False

    def run_rendering(self, term: Terminal, echo: Callable[[str], None]) -> None:
        """Runs the menu rendering with the user select highlighted and indexed items"""
        background_colour = term.black_on_skyblue
        menu_list = self.behaviour.menu_list

        # get the whitespace to center text from the largest line
        # - 3 to account for the index number added on to each
        max_line: str = max(menu_list)
        center_whitespace = ((term.width - len(max_line) - 3) // 2) * " "

        # add the background colour and title
        echo(f"{term.home}{background_colour}{term.clear}")
        echo(term.center(term.darkblue_underline(self.behaviour.title)).rstrip())

        # take the len of the list into account for y positioning
        first_option_line = (term.height - len(menu_list)) // 2
        echo(term.move_y(first_option_line) + "\n")

        for index, item in enumerate(menu_list):

            if index == self.selected:
                echo(
                    background_colour
                    + center_whitespace
                    + term.darkblue_reverse(f"{index+1}. {item}").rstrip()
                    + "\n"
                )
            else:
                echo(
                    background_colour
                    + center_whitespace
                    + f"{index+1}. {item}".rstrip()
                    + "\n"
                )

        echo(term.normal)

    def handle_stop(self) -> object:
        """Handles the menu on stop which returns the functionality in the current menus behaviour"""
        return self.behaviour.next_command(self.selected, self.character_emoji)
