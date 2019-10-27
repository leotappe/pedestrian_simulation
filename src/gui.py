"""
Graphical user interface for pedestrian simulation.
"""
import json
import tkinter as tk
from tkinter import filedialog
import simulation


CELL_SIZE = 20

COLORS = {
    simulation.EMPTY: 'white',
    simulation.PEDESTRIAN: 'red',
    simulation.OBSTACLE: 'blue',
    simulation.TARGET: 'green'
}


def display():
    """
    Create a GUI that allows the user to pick a scenario and step through it.
    """
    # Get filename from user
    filename = filedialog.askopenfilename(initialdir='data/')

    # Create system from file contents
    with open(filename) as file:
        scenario = json.load(file)
    rows, cols = scenario['rows'], scenario['cols']
    system = simulation.System(rows, cols)

    for pos in scenario['pedestrians']:
        system.add_pedestrian(*pos)

    for pos in scenario['obstacles']:
        system.add_obstacle(*pos)

    system.add_target(*scenario['target'])

    # Flood cells of system using Dijkstra
    system.dijkstra()

    # Root GUI widget
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Canvas for displaying grid
    width, height = cols * CELL_SIZE, rows * CELL_SIZE
    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()

    # Button for advancing the system state
    button = tk.Button(root, text='Step',
                       command=lambda: update_canvas(canvas, system))
    button.pack()

    # Draw initial system state
    update_canvas(canvas, system)

    root.mainloop()


def update_canvas(canvas, system):
    """
    Update the canvas and advance the system by one step.
    """
    for row in system.grid:
        for cell in row:
            x_top = cell.col * CELL_SIZE
            y_top = cell.row * CELL_SIZE
            x_bot = (cell.col + 1) * CELL_SIZE
            y_bot = (cell.row + 1) * CELL_SIZE
            color = COLORS[cell.state]
            canvas.create_rectangle(x_top, y_top, x_bot, y_bot, fill=color)

    system.step()
