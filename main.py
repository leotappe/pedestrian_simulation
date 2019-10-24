import json
import collections
import math


EMPTY = 0
PEDESTRIAN = 1
OBSTACLE = 2
TARGET = 3
INF = 10**10


class System:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[Cell(i, j) for j in range(cols)] for i in range(rows)]
        self.target = None
        self.pedestrians = []

    def add_target(self, row, col):
        if self.target is not None:
            self.target.state = EMPTY
        self.grid[row][col].state = TARGET
        self.target = self.grid[row][col]

    def add_pedestrian(self, row, col):
        self.grid[row][col].state = PEDESTRIAN
        self.pedestrians.append(self.grid[row][col])

    def add_obstacle(self, row, col):
        self.grid[row][col].state = OBSTACLE

    def compute_distances(self):
        self.target.distance = 0
        deque = collections.deque([self.target])

        while deque:
            cell = deque.pop()

            for neighbor in self.get_neighbors(cell, [OBSTACLE]):
                if cell.distance + 1 < neighbor.distance:
                    neighbor.distance = cell.distance + 1
                    deque.appendleft(neighbor)

    def get_neighbors(self, cell, blacklist):
        deltas = [-1, 0, 1]

        return [self.grid[cell.row + d_row][cell.col + d_col]
                for d_row in deltas for d_col in deltas
                if 0 <= cell.row + d_row < self.rows and
                0 <= cell.col + d_col < self.cols and
                (d_row != 0 or d_col != 0) and
                self.grid[cell.row + d_row][cell.col + d_col].state not in blacklist]

    def step(self):
        for p in self.pedestrians:
            self.add_penalty(p)

        next_cells = []
        for p in self.pedestrians:
            next_cells.append(min(self.get_neighbors(p, [PEDESTRIAN, OBSTACLE]),
                                  key=lambda cell: cell.distance + cell.penalty))

        for p in self.pedestrians:
            self.add_penalty(p, negative=True)

        new_pedestrians = []
        for p, next_cell in zip(self.pedestrians, next_cells):
            if next_cell.state == EMPTY:
                p.state = EMPTY
                next_cell.state = PEDESTRIAN
                new_pedestrians.append(next_cell)
            else:
                new_pedestrians.append(p)

        self.pedestrians = new_pedestrians

    def print_grid(self):
        for row in self.grid:
            print(''.join(str(cell) for cell in row))

    def print_distances(self):
        for row in self.grid:
            for cell in row:
                print(f'{cell.distance:02d} ', end=' ')
            print()

    def add_penalty(self, cell, d_max=3, negative=False):
        for row in range(max(0, cell.row - d_max), min(self.rows - 1, cell.row + d_max)):
            for col in range(max(0, cell.col - d_max), min(self.cols - 1, cell.col + d_max)):
                d = min(abs(cell.row - row), abs(cell.col - col))
                self.grid[row][col].penalty -= (-1)**negative * math.exp(1 / (d**2 - (d_max + 1)**2))


class Cell:
    def __init__(self, row, col, state=EMPTY):
        self.state = state
        self.row = row
        self.col = col
        self.penalty = 0
        self.distance = INF

    def __str__(self):
        symbols = {
            EMPTY: '.',
            PEDESTRIAN: 'P',
            OBSTACLE: 'O',
            TARGET: 'T'
        }
        return symbols[self.state]


def main():
    filename = 'data/task3.json'
    with open(filename) as file:
        scenario = json.load(file)
    rows, cols = scenario['rows'], scenario['cols']
    system = System(rows, cols)

    for pos in scenario['pedestrians']:
        system.add_pedestrian(*pos)

    for pos in scenario['obstacles']:
        system.add_obstacle(*pos)

    system.add_target(*scenario['target'])
    system.print_grid()

    system.compute_distances()

    num_steps = 21
    print(f'Simulating {num_steps} steps')
    for _ in range(num_steps):
        system.step()

    system.print_grid()


if __name__ == '__main__':
    main()
