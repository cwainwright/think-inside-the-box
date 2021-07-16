#
# Created on Wed Jul 14 2021
#
# The MIT License
# -----------
# Copyright (c) 2021 Alan O'Regan, Condar, cwainwright, Geekid, tooboredtocode(albedo)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from queue import Queue
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

from blessed import Terminal
from blessed.keyboard import Keystroke

from base import GameSection
from commands import EndGame, ChangeSection


class MenuType:
    pass


@dataclass
class StartMenuType(MenuType):
    character: str = '🙂'


@dataclass
class CharacterMenuType(MenuType):
    character: str


class StartMenuBehaviour:
    title = 'Start Menu'
    menu_list = [
        'Play',
        'Character Select',
        'Quit',
    ]

    def initial_selection(self, _):
        return 0

    def is_valid_selection(self, index):
        return index in range(len(self.menu_list))

    def next_command(self, index, character):
        if index == 0:
            return ChangeSection('over_world', object())

        if index == 1:
            return ChangeSection('menu', CharacterMenuType(character))

        if index == 2:
            return EndGame()


class CharacterMenuBehaviour:
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

    def initial_selection(self, character):
        return self.menu_list.index(character)

    def is_valid_selection(self, index):
        return index in range(len(self.menu_list))

    def next_command(self, index, _):
        return ChangeSection('menu', StartMenuType(self.menu_list[index]))


class Menu(GameSection):
    """
    Class for Menu System

        - display(list[]) "Dislays menu from given dictionary"
        - get_choice() "Returns the most recent choice from the Menu object"
    """

    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)
        self.character_emoji = "🙂"

    def handle_start(self, start_data: MenuType):
        behaviour_class = {
            StartMenuType: StartMenuBehaviour,
            CharacterMenuType: CharacterMenuBehaviour,
        }[type(start_data)]
        self.behaviour = behaviour_class()
        self.selected = self.behaviour.initial_selection(self.character_emoji)

        try:
            self.character_emoji = start_data.character
        except AttributeError:
            pass

    def run_processing(self, input: Optional[Keystroke]) -> bool:
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

    def run_rendering(self, term: Terminal, echo: Callable[[str], None]):
        # add the background colour and title
        echo(f"{term.home}{term.black_on_skyblue}{term.clear}")
        echo(term.center(term.bold_underline(self.behaviour.title)).rstrip())

        # take the len of the list into account for y positioning
        menu_list = self.behaviour.menu_list
        first_option_line = (term.height - len(menu_list)) // 2
        echo(term.move_y(first_option_line) + "\n")

        echo(term.black_on_skyblue)

        for index, item in enumerate(menu_list):
            if index == self.selected:
                echo(term.center(term.darkblue_reverse(f"{index+1}. {item}")).rstrip() + "\n")
            else:
                echo(term.center(f"{index+1}. {item}").rstrip() + "\n")

        echo(term.normal)

    def handle_stop(self) -> object:
        return self.behaviour.next_command(self.selected, self.character_emoji)
