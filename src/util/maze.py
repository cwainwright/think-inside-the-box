import random


def generate(m: int, n: int) -> list[list[bool]]:
    """Implementation of the randomized Prim's algorithm for maze generation"""
    mm, nn = m - 3, n - 3
    x, y = random.randint(0, mm), random.randint(0, nn)

    def in_grid(x: int, y: int) -> bool:
        return 0 <= x <= mm and 0 <= y <= nn

    def get_neighbours(x: int, y: int) -> set[tuple[int, int]]:
        return {(x + i, y + j) for i, j in [[1, 0], [-1, 0], [0, 1], [0, -1]] if in_grid(x + i, y + j)}

    floors = {(x, y)}
    walls = [(xx, yy) for xx, yy in get_neighbours(x, y) if 0 <= xx <= mm and 0 <= yy <= nn]

    while walls:
        x, y = random.choice(walls)
        walls.remove((x, y))
        neighbours = get_neighbours(x, y)
        if len(neighbours & floors) == 1:
            floors.add((x, y))
            walls += [neighbour for neighbour in neighbours if neighbour not in walls]

    floors = {(x + 1, y + 1) for x, y in floors}

    start_x = random.choice([x for x in range(m) if (x, 1) in floors])
    end_x = random.choice([x for x in range(n) if (x, n-2) in floors])

    floors.add((start_x, 0))
    floors.add((end_x, n - 1))

    return maze_as_array(m, n, floors)


def maze_as_array(
        m: int,
        n: int,
        floors: set[tuple[int, int]],
) -> list[list[bool]]:
    """Generates and returns maze in matrix form"""
    matrix = []
    for y in range(n):
        row = []
        for x in range(m):
            tile = True if (x, y) in floors else False
            row.append(tile)
        matrix.append(row)
    return matrix
