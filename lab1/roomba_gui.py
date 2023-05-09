from __future__ import annotations
from typing import *
from tkinter import filedialog, Tk
from os import getcwd
from sys import argv
from roomba_problem import *
from roomba_heuristics import ROOMBA_HEURISTICS
from search_algorithms import ALGORITHMS, STRATEGIES
from search_gui import Search_GUI, Search_GUI_Controller

# State visualization too big? Change these numbers
MAX_HEIGHT = 350
MAX_WIDTH = 450

PATH, AGENT, START, SEEN = 'path', 'agent', 'start', 'seen'
# TEXT = 'text'
COLORS: Dict[Union[Terrain, str], str] = {FLOOR: 'pale green', CARPET: 'RoyalBlue1', WALL: 'gray25',
                                          DIRTY_FLOOR: 'brown', DIRTY_CARPET: 'saddle brown',
                                          AGENT: "orange red", START: 'IndianRed1', PATH: 'IndianRed1', SEEN: 'black',
                                          #   TEXT: 'black'
                                          }


class Roomba_GUI(Search_GUI):

    current_state: RoombaState

    def __init__(self, initial_state: RoombaState, algorithm_names: Sequence[str], strategy_names: Sequence[str], heuristics: Dict[str, Callable[[StateNode], float]]):
        self.width = initial_state.get_width()
        self.height = initial_state.get_height()
        if self.width / self.height > MAX_WIDTH / MAX_HEIGHT:
            canvas_width = MAX_WIDTH
            canvas_height = MAX_WIDTH * self.height // self.width
        else:
            canvas_height = MAX_HEIGHT
            canvas_width = MAX_HEIGHT * self.width // self.height
        super().__init__(canvas_height=canvas_height, canvas_width=canvas_width,
                         algorithm_names=algorithm_names, strategy_names=strategy_names, heuristics=heuristics)
        self.title("Roomba Search Visualizer")

    def calculate_box_coords(self, coord: Coordinate) -> Tuple[int, int, int, int]:
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        x1 = w * coord.col // self.width
        y1 = h * coord.row // self.height
        x2 = w * (coord.col + 1) // self.width
        y2 = h * (coord.row + 1) // self.height
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, coord: Coordinate) -> Tuple[int, int]:
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        x = int(w * (coord.col + .5)) // self.width
        y = int(h * (coord.row + .5)) // self.height
        return (x, y)

    # Override
    def draw_state(self):
        self.canvas.delete(AGENT)

        # roomba agent
        x1, y1, x2, y2 = self.calculate_box_coords(self.current_state.position)
        self.canvas.create_oval((x1, y1, x2, y2), fill='',
                                outline=COLORS[SEEN], tags=SEEN)
        self.canvas.create_oval(x1, y1, x2, y2, fill=COLORS[AGENT], tags=AGENT)

        self.canvas.delete(PATH)
        self.canvas.delete(START)
        if self.current_state.depth > 0:
            self.draw_path()
        else:
            self.canvas.delete(SEEN)  # This is a bit of a hack...

    # Override
    def draw_path(self):
        # needed a cast here, since get_path() returns : Sequence[StateNode]
        path = cast(Sequence[RoombaState], self.current_state.get_path())
        path_coords = [self.calculate_center_coords(state.position)
                       for state in path]
        # This line breaks the type checkers, but create_line will flatten the list of tuples..
        self.canvas.create_line(
            path_coords, fill=COLORS[PATH], width=3, tags=PATH, )  # type: ignore

        # Draw outline of initial roomba position at the start of the path
        self.canvas.create_oval(self.calculate_box_coords(
            path[0].position), fill='', outline=COLORS[START], tags=START)

    # Override
    def draw_background(self):

        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas

        # Clear the background grid and terrain
        self.canvas.delete('grid_line')
        self.canvas.delete('terrain_block')

        # Creates all vertical lines
        for c in range(0, self.width):
            x = w * c // self.width
            self.canvas.create_line((x, 0, x, h), tags='grid_line')

        # Creates all horizontal lines
        for r in range(0, self.height):
            y = h * r // self.height
            self.canvas.create_line((0, y, w, y), tags='grid_line')

        # Draw terrain
        maze = self.current_state.grid
        for r in range(0, self.height):
            for c in range(0, self.width):
                self.canvas.create_rectangle(
                    *self.calculate_box_coords(Coordinate(r, c)), fill=COLORS[maze[r][c]], tags='terrain_block')

    def click_canvas_to_action(self, event) -> RoombaAction:
        w = self.canvas.winfo_width()  # Get current width of canvas
        col = event.x // (w // self.width)
        h = self.canvas.winfo_height()  # Get current height of canvas
        row = event.y // (h // self.height)
        pos = self.current_state.position
        return RoombaAction(row - pos.row, col - pos.col)


if __name__ == "__main__":
    if len(argv) > 1:
        file_path = argv[1]
    else:
        initroot = Tk()
        initroot.withdraw()
        file_path = filedialog.askopenfilename(title="Open Roomba File", initialdir=getcwd(
        ), filetypes=[("Roomba", ".roomba"), ("Text", ".txt")])
        initroot.destroy()
    initial_state = RoombaState.readFromFile(file_path)
    gui = Roomba_GUI(initial_state, algorithm_names=list(ALGORITHMS.keys(
    )), strategy_names=list(STRATEGIES.keys()), heuristics=ROOMBA_HEURISTICS)
    controller = Search_GUI_Controller(gui, initial_state, ROOMBA_HEURISTICS)
    gui.mainloop()
