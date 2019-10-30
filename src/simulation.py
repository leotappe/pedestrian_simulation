"""
Pedestrian simulation based on cellular automata.
"""
import collections
import math
import heapq


EMPTY = 0
PEDESTRIAN = 1
OBSTACLE = 2
TARGET = 3
INF = 10**10


class System:
    """
    A grid of cells.
    """
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[Cell(i, j) for j in range(cols)] for i in range(rows)]
        self.target = None
        self.pedestrians = []
        self.obstacles = []

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
        self.obstacles.append(self.grid[row][col])

    def compute_distances(self):
        """
        Deprecated, doesn't use euclidean distance.
        """
        self.target.distance = 0
        deque = collections.deque([self.target])

        while deque:
            cell = deque.pop()

            for neighbor in self.get_neighbors(cell, [OBSTACLE]):
                if cell.distance + 1 < neighbor.distance:
                    neighbor.distance = cell.distance + 1
                    deque.appendleft(neighbor)

    def dijkstra(self):
        """
        Flood the cells with distance values to the target using Dijkstra
        Algorithm.
        """
        self.target.distance = 0
        priority_queue = [(0, self.target)]

        while priority_queue:
            distance, cell = heapq.heappop(priority_queue)
            if distance > cell.distance:
                continue

            for neighbor in self.get_neighbors(cell, [OBSTACLE]):
                distance = euclidean_distance(cell, neighbor)
                if cell.distance + distance < neighbor.distance:
                    neighbor.distance = cell.distance + distance
                    heapq.heappush(priority_queue, (neighbor.distance, neighbor))

    def get_neighbors(self, cell, blacklist):
        """
        Return a list of cells which are adjacent to the given cell, within
        bounds, and in a state which is not blacklisted.
        """
        deltas = [-1, 0, 1]

        return [self.grid[cell.row + d_row][cell.col + d_col]
                for d_row in deltas for d_col in deltas
                if 0 <= cell.row + d_row < self.rows and
                0 <= cell.col + d_col < self.cols and
                (d_row != 0 or d_col != 0) and
                self.grid[cell.row + d_row][cell.col + d_col].state not in blacklist]

    def step(self):
        """
        Advance the system by one step.
        """
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
        """
        Print the grid's cell's contents.
        """
        for row in self.grid:
            print(''.join(str(cell) for cell in row))

    def print_distances(self):
        """
        Print the grid's distance values.
        """
        for row in self.grid:
            for cell in row:
                print(f'{cell.distance:02d} ', end=' ')
            print()

    def print_penalties(self):
        for row in self.grid:
            for cell in row:
                if cell.penalty > 0:
                    print(f'{cell.penalty:.2f}', end=' ')
                else:
                    print('    ', end=' ')
            print()

    def add_penalty(self, cell, d_max=3, negative=False):
        """
        Add a cost penalty to the cells within d_max of this cell.
        """
        for row in self.grid[max(0, cell.row - d_max):min(self.rows, cell.row + d_max + 1)]:
            for other_cell in row[max(0, cell.col - d_max):min(self.cols, cell.col + d_max + 1)]:
                distance = euclidean_distance(cell, other_cell)
                if distance < d_max:
                    other_cell.penalty += (-1)**negative * math.exp(1 / (distance**2 - d_max**2))


class Cell:
    """
    A cell of the system.
    """
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

    def __lt__(self, other):
        return self.distance < other.distance


def euclidean_distance(cell_1, cell_2):
    return math.sqrt((cell_1.row - cell_2.row)**2 + (cell_1.col - cell_2.col)**2)