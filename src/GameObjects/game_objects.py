'''Includes all object classes that appear in-game'''
import json
import random
from copy import deepcopy
from pathlib import Path



def four_way_junction_matcher(entrances_exits):
    '''Check existence of 4-way-junction'''
    if entrances_exits.count(True) == 4:
        return {
            "type":"4-way-junction",
            "rotation":0
        }

    return None

def three_way_junction_matcher(entrances_exits):
    '''Check existence and rotation of 3-way-junction'''
    if entrances_exits.count(True) != 3:
        return None

    sequence = [True, True, True, False]
    for index in range(4):
        if sequence == entrances_exits:
            return {
                "type":"3-way-junction",
                "rotation":90*index
            }
        sequence = sequence[-1:]+sequence[:-1]

    return None

def corner_matcher(entrances_exits):
    if entrances_exits.count(True) != 2:
        return None

    sequence = [True]*2 + [False]*2
    for index in range(4):
        if sequence == entrances_exits:
            return {
                "type":"corner",
                "rotation":90*index
            }
        sequence = sequence[-1:]+sequence[:-1]

    return None

def straight_matcher(entrances_exits):
    if entrances_exits.count(True) != 2:
        return None

    if [True, False]*2 == entrances_exits:
        return {
            "type":"straight",
            "rotation":0
        }
    else:
        return {
            "type":"straight",
            "rotation":90
        }

def dead_end_matcher(entrances_exits):
    if entrances_exits.count(True) != 1:
        return None
    
    sequence = [True] + [False]*3
    for index in range(4): 
        if sequence == entrances_exits:
            return {
                "type":"dead-end",
                "rotation":90*index
            }
        sequence = sequence[-1:]+sequence[:-1]

# World Data class
class World:
    '''Container for world/level - contains all rooms initialised'''
    def __init__(self, maze_matrix, term):
        self.raw_matrix = maze_matrix
        self.terminal = term
        #Find entrance (bottom) exit (top)
        self.maze_data = {
            "length":len(self.raw_matrix),
            "width":len(self.raw_matrix[0]),
            "entrance_index":self.raw_matrix[0].index(True),
            "exit_index":self.raw_matrix[-1].index(True)
        }
        self.world_matrix = self.convert_matrix()
        self.update_world_location(0, self.maze_data["entrance_index"])

    def convert_matrix(self) -> list[list]:
        '''Converts maze_matrix from maze.py to list of rooms'''
        world_list = []
        for row_index in range(self.maze_data["length"]):
            row = []
            for column_index in range(self.maze_data["width"]):
                if row_index in [0, self.maze_data["length"]-1] or column_index in [0, self.maze_data["width"]-1]:
                    print(column_index, row_index, end=":")
                    print("Empty")
                    row.append(Empty())
                else:
                    print(column_index, row_index, end=":")
                    entrances_exits = [
                        self.raw_matrix[row_index-1][column_index],
                        self.raw_matrix[row_index][column_index+1],
                        self.raw_matrix[row_index+1][column_index],
                        self.raw_matrix[row_index][column_index-1]
                    ]
                    print(entrances_exits, end=" - ")
                    if self.raw_matrix[row_index][column_index]:
                        matchers = [
                            four_way_junction_matcher,
                            three_way_junction_matcher,
                            corner_matcher,
                            straight_matcher,
                            dead_end_matcher
                        ]

                        for matcher in matchers:
                            result = matcher(entrances_exits)
                            if result is not None:
                                room_parameters = result
                                break

                        print("Room:"+str(room_parameters))

                        row.append(Room(
                            room_parameters["type"],
                            room_parameters["rotation"],
                            self.terminal,
                        ))
                    else:
                        print("Empty")
                        row.append(Empty())
            world_list.append(row)
            print()
        world_list[0][self.maze_data["entrance_index"]] = Room("dead-end", 180, self.terminal)
        world_list[-1][self.maze_data["exit_index"]] = Room("dead-end", 0, self.terminal)
        return world_list

    def update_world_location(self, r_location, c_location):
        self.world_location = [r_location, c_location]
        self.active_room = self.world_matrix[r_location][c_location]
        return not self.world_location[0] == 9

# Room Data classes
class Tile:
    '''
    Parent class definition of Tile
    '''
    def __init__(self, vacant):
        self.vacant = vacant
        file_path = Path(__file__).parent / 'object_representation.json'
        with file_path.open('r', encoding='utf8') as object_representation_file:
            self.object_representation_json = json.load(object_representation_file)
        self.representation = ""

    def __str__(self):
        return self.representation

class Wall(Tile):
    '''
    Class definition of Wall Tile
    Subclass of Tile class
    '''
    def __init__(self):
        super().__init__(False)
        self.representation = self.object_representation_json["Wall"]

class Space(Tile):
    '''
    Class definition of Space Tile
    Subclass of Tile class
    '''
    def __init__(self):
        super().__init__(True)
        self.representation = self.object_representation_json["Space"]

class Door(Tile):
    '''
    Class definition of Door Tile
    Subclass of Tile class
    '''
    def __init__(self, locked):
        super().__init__(True)
        self.locked=locked
        self.representation_selection = self.object_representation_json["Door"]

    def lock_unlock(self):
        '''Toggle locked state'''
        self.locked = not self.locked

    def enter(self):
        '''Return whether or not player is permitted to enter'''
        return not self.locked

    def __str__(self):
        return self.representation_selection[int(self.locked)]

class Empty:
    '''Literally nothingness, a wall in the world'''
    def __init__(self):
        self.representation = "E"

    def __str__(self):
        return self.representation


class Room:
    '''
    Class definition of Room
    For simplicity, grid size will always have dimensions of 9*9 (excluding walls)
    '''
    def __init__(
        self,
        room_type,
        rotation,
        term,
        room_templates_filepath=Path(__file__).parent / 'room_templates.json'
    ):
        accepted_room_types = ["dead-end", "straight", "corner", "3-way-junction","4-way-junction"]
        self.room_type = room_type if room_type in accepted_room_types else "straight"
        self.term = term
        self.rotation = rotation
        self.display_array = []
        self.entity_dict = {}
        self.tiles = []
        self.representation = "R"
        # Use JSON file to generate Room grid layout
        with room_templates_filepath.open('r', encoding='utf8') as room_templates:
            template = random.choice(json.load(room_templates)[self.room_type])["layout"]
        # Rotate template (if necessary) [0, 90, 180, 270]
        for _ in range(rotation//90):
            template = list(zip(*template[::-1]))
        #Map template spaces to Tiles in Room
        for y_coord in template:
            row = []
            for x_coord in y_coord:
                # Anyone know how to implement a switch statement in Python?
                if x_coord == "#":
                    row.append(str(Wall()))
                elif x_coord == " ":
                    row.append(str(Space()))
                elif x_coord == "/":
                    row.append(str(Door(locked=False)))
                elif x_coord == "|":
                    row.append(str(Door(locked=True)))
                else:
                    row.append(str(Space()))
            self.tiles.append(row)
        placements = random.choice([(5, 1), (9, 5), (5, 9), (1, 5)])
        self.add_entity(
            "Enemy"+str(placements),
            NPC(placements[0], placements[1])
        )

    def add_entity(self, entity_name: str, entity):
        '''Adds entity object to Room'''
        can_add = True
        for entities in self.entity_dict.values():
            can_add = entity.get_location() != entities.get_location()
        if can_add:
            self.entity_dict.update({entity_name: entity})

    def update_display(self):
        '''combines tiles and entities to update display'''
        self.display_array = deepcopy(self.tiles)
        for entities in self.entity_dict.values():
            location = entities.get_location()
            self.display_array[location[1]][location[0]] = str(entities)

    def display(self):
        '''Display room'''
        with self.term.cbreak(), self.term.hidden_cursor():
            keystroke = None
            while keystroke != "KEY_ESCAPE":
                self.update_display()
                print(f"{self.term.home}{self.term.white_on_black}{self.term.clear}")

                for row in self.display_array:
                    print(self.term.center("".join(row)))

                keystroke = self.term.inkey(timeout=3)
                up, left, down, right = [False]*4
                if keystroke.name == "KEY_UP":
                    up = self.move_entity("up", "player")
                    print(self.term.center("up"))
                elif keystroke.name == "KEY_LEFT":
                    left = self.move_entity("left", "player")
                    print(self.term.center("left"))
                elif keystroke.name == "KEY_DOWN":
                    down = self.move_entity("down", "player")
                    print(self.term.center("down"))
                elif keystroke.name == "KEY_RIGHT":
                    right = self.move_entity("right", "player")
                    print(self.term.center("right"))
                elif keystroke.name == "KEY_TAB":
                    adjacent_npc = self.scan_for_adjacent_NPC()
                    try:
                        if adjacent_npc[1].ask_question():
                            if adjacent_npc[1].get_location() == [9,5]:
                                direction = "up"
                            elif adjacent_npc[1].get_location() == [5,9]:
                                direction = "left"
                            elif adjacent_npc[1].get_location() == [1,5]:
                                direction = "down"
                            elif adjacent_npc[1].get_location() == [5,1]:
                                direction = "right"

                    except TypeError:
                        pass
                    else:
                        if adjacent_npc[1].get_location() in [[9,5],[5,9],[1,5],[5,1]]:
                            self.move_entity(direction, adjacent_npc[0])

                player_location_x, player_location_y = self.entity_dict["player"].get_location()
                if player_location_x in [0, 10] or player_location_y in [0, 10]:
                    return [{up:"up", left:"left", down:"down", right:"right"}[True], self.entity_dict["player"]]

    def move_entity(self, direction, entity_name):
        '''Alter coord of entity in self.entity_dict'''
        translation = {"up":(0, -1),"left":(-1, 0),"down":(0, 1),"right":(1, 0)}[direction]
        entity = self.entity_dict[entity_name]
        location = entity.get_location()
        x_translated = int(location[0]+translation[0])
        y_translated = int(location[1]+translation[1])
        #Detect entities in translation space
        for entities in self.entity_dict.items():
            if entities[0] != "player":
                space_vacancy = [x_translated, y_translated] != entities[1].get_location()
        print(self.term.center(entity.get_location()))
        print(self.term.center(direction))
        print(self.term.center({True:"Space vacant", False:"Space not vacant"}[space_vacancy]))
        if x_translated in range(0, 11) and y_translated in range(0, 11):
            tile_vacancy = self.tiles[y_translated][x_translated] in ["  ", "//"]
            print(self.term.center({True:"Tile vacant", False:"Tile not vacant"}[tile_vacancy]))
        else:
            tile_vacancy = False
            print(self.term.center("Tile out of range"))
        if tile_vacancy and space_vacancy:
            entity.update_location(x_translated, y_translated)
            return True
        else:
            return False

    def __str__(self):
        return self.representation

    def scan_for_adjacent_NPC(self):
        location = self.entity_dict["player"].get_location()
        adjacent_spaces = [
            [location[0], location[1]+1],
            [location[0]+1, location[1]],
            [location[0], location[1]-1],
            [location[0]-1, location[1]]
        ]
        for entities in self.entity_dict.items():
            if entities[0] != "player" and entities[1].get_location() in adjacent_spaces:
                return entities
        return None

# Entity Data classes
class Entity:
    '''
    Class definition of Entity Superclass
    '''
    def __init__(self, x_location: int, y_location: int):
        self.location = [x_location, y_location]
        self.tile_location = [10-y_location, x_location]
        object_representation_filepath=Path(__file__).parent / 'object_representation.json'
        with object_representation_filepath.open('r', encoding='utf8') as object_representation_file:
            self.object_representation_json = json.load(object_representation_file)
        self.representation = ""

    def get_location(self):
        '''Returns location data (x, y)'''
        return self.location

    def get_tile_location(self):
        '''Returns tile location data (y, 10-x)'''
        return self.tile_location

    def update_location(self, x_location: int = None, y_location: int = None):
        '''Updates location data'''
        if x_location is not None and x_location>=0 and x_location<=10:
            self.location[0] = x_location
        if y_location is not None and y_location>=0 and y_location<=10:
            self.location[1] = y_location
        self.tile_location = [self.location[1], 10-self.location[0]]

    def __str__(self):
        return self.representation

# class Riddle:
#     '''
#     Riddle class on initialisation take in no additional parameters
#     Randomly selects riddle
#     Stores answer securely using encapsulation
#     '''
#     def __init__(self):
#         with open("riddles.json") as riddles_file:
#             chosen_riddle=random.choice(json.load(riddles_file))
#         self.__question=chosen_riddle["question"]
#         self.__answers=chosen_riddle["answers"]
#         self.__correct_answer=chosen_riddle["correct_answer"]

#    def return_question(self):
#        '''
#        Returns question and answers
#        '''
#        return(self.__question, self.__answers)

#    def check_answer(self, player_answer):
#        '''
#        Takes player answer parameter
#        Returns bool result
#        '''
#        return player_answer == self.__correct_answer


class NPC(Entity):
    '''
    Class definition of NPC Entity
    '''
    def __init__(self, x_location: int, y_location: int):
        super().__init__(x_location, y_location)
        super().get_location()
        super().update_location()
        self.representation = self.object_representation_json["NPC"]

    def ask_question(self):
        print("Takeover")
        return(True or False)
#        self.riddle = Riddle()

#    def ask_riddle(self):
#        '''Returns riddle question'''
#        return self.riddle.return_question()
#
#    def answer_riddle(self, player_answer):
#        '''Returns riddle answer result'''
#        return self.riddle.check_answer(player_answer)

class Player(Entity):
    '''
    Class definition of Player Entity
    '''
    def __init__(self, x_location: int, y_location: int):
        super().__init__(x_location, y_location)
        super().get_location()
        super().update_location()
        self.representation = self.object_representation_json["Player"]