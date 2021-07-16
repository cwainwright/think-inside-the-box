'''Experimental script for testing game_objects in a visual environment'''
from blessed import Terminal
from game_objects import World, Player

maze_matrix_test = [
    [False, False, False, False, False, False, False, False, True,  False],
    [False, False, True,  True,  True,  True,  True,  True,  True,  False],
    [False, True,  False, False, True,  False, True,  False, True,  False],
    [False, True,  False, True,  False, True,  True,  True,  False, False],
    [False, True,  True,  True,  True,  True,  False, False, True,  False],
    [False, True,  False, True,  False, True,  True,  True,  True,  False],
    [False, False, True,  True,  False, True,  False, False, True,  False],
    [False, True,  False, False, True,  True,  True,  True,  False, False],
    [False, True,  True,  True,  True,  False, True,  False, False, False],
    [False, False, False, True,  False, False, False, False, False, False]
]

#Initial Room
term = Terminal()
world = World(maze_matrix_test, term)
for line in world.world_matrix:
    display_room_line = []
    for item in line:
        display_room_line.append(str(item))
    print(display_room_line)
world.active_room.add_entity("player", Player(5, 1))
room_directions = {"up":(-1, 0),"left":(0, -1),"down":(1, 0),"right":(0, 1)}
player_directions = {"up":(5, 9),"left":(9, 5),"down":(5, 1),"right":(1, 5)}
not_end = True
while not_end:
    room_bearing, player = world.active_room.display()
    translation_r, translation_c = room_directions[room_bearing]
    not_end = world.update_world_location(
        world.world_location[0]+translation_r,
        world.world_location[1]+translation_c
    )
    player_x, player_y = player_directions[room_bearing]
    print(world.world_location)
    print(world.active_room)
    world.active_room.add_entity("player", player)
    world.active_room.entity_dict["player"].update_location(player_x, player_y)
