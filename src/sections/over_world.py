from dataclasses import dataclass
from queue import Queue
from typing import Callable, Optional, Union

from blessed import Terminal
from blessed.keyboard import Keystroke

from src.commands import ChangeSection, EndGame
from src.GameObjects.game_objects import World
from src.sections.base import GameSection
from src.sections.question import NewQuestion, QuestionResult
from src.util import maze


@dataclass
class StartOverWorld:
    """Dataclass to indicate starting the overwold"""

    character: str
    reset_character: bool


class OverWorld(GameSection):
    """Over world game section"""

    def __init__(self, in_queue: Queue):
        super().__init__(in_queue)
        world_maze = maze.generate(10, 10)
        print(world_maze)
        self.world = World(world_maze)
        self.npc = None

    def handle_start(self, start_data: Union[StartOverWorld, QuestionResult]) -> bool:
        """Inherit"""
        try:
            reset_character = not start_data.was_correct
        except AttributeError:
            reset_character = start_data.reset_character

        if reset_character:
            self.world.reset_to_start()
        else:
            npc_location = tuple(self.npc.get_location())
            if npc_location == (9, 5):
                direction = "up"
            elif npc_location == (5, 9):
                direction = "left"
            elif npc_location == (1, 5):
                direction = "down"
            elif npc_location == (5, 1):
                direction = "right"

            try:
                self.world.active_room.move_entity(direction, f'enemy{npc_location}')
            except NameError:
                pass

        self.npc = None

        return True

    def run_processing(self, inp: Optional[Keystroke]) -> bool:
        """Inherit"""
        if inp is None:
            return False

        room = self.world.active_room
        player_move_direction = None

        if inp.name == "KEY_UP":
            player_move_direction = room.move_entity("up", "player") and "up"
        elif inp.name == "KEY_LEFT":
            player_move_direction = room.move_entity("left", "player") and "left"
        elif inp.name == "KEY_DOWN":
            player_move_direction = room.move_entity("down", "player") and "down"
        elif inp.name == "KEY_RIGHT":
            player_move_direction = room.move_entity("right", "player") and "right"
        elif inp.name == "KEY_TAB":
            adjacent_npc = room.scan_for_adjacent_NPC()
            if adjacent_npc is not None:
                self.stop()
                self.npc = adjacent_npc[1]
            # else:
            #     if adjacent_npc[1].get_location() in [[9, 5], [5, 9], [1, 5], [5, 1]]:
            #         self.move_entity(direction, adjacent_npc[0])

        player = self.world.active_room.entity_dict['player']
        player_location_x, player_location_y = player.get_location()

        if player_move_direction is not None:
            if player_location_x in [0, 10] or player_location_y in [0, 10]:
                self.world.update_world_location(
                    self.world.world_location[0] + {'up': -1, 'down': 1}.get(player_move_direction, 0),
                    self.world.world_location[1] + {'left': -1, 'right': 1}.get(player_move_direction, 0),
                )
                self.world.active_room.add_entity('player', player)
                self.world.active_room.entity_dict['player'].update_location(
                    *{'up': (5, 9), 'right': (1, 5), 'down': (5, 1), 'left': (9, 5)}[player_move_direction]
                )
            return True

        return False

    def run_rendering(self, terminal: Terminal, echo: Callable[[str], None]) -> None:
        """Inherit"""
        self.world.active_room.update_display()
        self.world.active_room.render(terminal, echo)

    def handle_stop(self) -> object:
        """Inherit"""
        if self.world.completed:
            return EndGame()
        else:
            return ChangeSection('question', NewQuestion())
