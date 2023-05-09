from __future__ import annotations
from typing import *
from tkinter import filedialog, Tk
from os import getcwd
from sys import argv
from slidepuzzle_problem import *
from slidepuzzle_heuristics import SLIDEPUZZLE_HEURISTICS
from search_algorithms import ALGORITHMS, STRATEGIES
from search_gui import Search_GUI, Search_GUI_Controller

# State visualization too big? Change these numbers
MAX_HEIGHT = 450
MAX_WIDTH = 450

TILE, EMPTY, PATH, TEXT = 'tile', 'empty', 'path', 'text'
COLORS = {TILE: 'tan', EMPTY: 'white', PATH: 'IndianRed1', TEXT: 'black'}


class SlidePuzzle_GUI(Search_GUI):

    current_state: SlidePuzzleState

    def __init__(self, initial_state: SlidePuzzleState, algorithm_names: Sequence[str], strategy_names: Sequence[str], heuristics: Dict[str, Callable[[StateNode], float]]):
        self.puzzle_dim = initial_state.get_size()
        super().__init__(canvas_height=MAX_HEIGHT, canvas_width=MAX_WIDTH,
                         algorithm_names=algorithm_names, strategy_names=strategy_names, heuristics=heuristics)
        self.title("Slide Puzzle Search Visualizer")

    def calculate_box_coords(self, coord: Coordinate) -> Tuple[int, int, int, int]:
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        x1 = w * coord.col // self.puzzle_dim
        y1 = h * coord.row // self.puzzle_dim
        x2 = w * (coord.col + 1) // self.puzzle_dim
        y2 = h * (coord.row + 1) // self.puzzle_dim
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, coord: Coordinate) -> Tuple[int, int]:
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        x = int(w * (coord.col + .5)) // self.puzzle_dim
        y = int(h * (coord.row + .5)) // self.puzzle_dim
        return (x, y)

    # Override
    def draw_state(self):
        self.canvas.delete(TEXT)
        self.canvas.delete(EMPTY)
        self.canvas.delete(PATH)

        # roomba agent

        # draw number tiles and empty tile
        text_size = self.canvas.winfo_height() // (self.puzzle_dim * 2)
        for r in range(0, self.puzzle_dim):
            for c in range(0, self.puzzle_dim):
                coord = Coordinate(r, c)
                tile = self.current_state.get_tile_at(coord)
                pos = self.calculate_center_coords(coord)
                if tile != 0:
                    self.canvas.create_text(pos, fill=COLORS[TEXT], tags=TEXT,
                                            text=str(tile), font=('Times New Roman', text_size, 'bold'))
                else:
                    x1, y1, x2, y2 = self.calculate_box_coords(coord)
                    self.canvas.create_rectangle(
                        x1+2, y1+2, x2-2, y2-2, fill=COLORS[EMPTY], tags=EMPTY)

        if self.current_state.depth > 0:
            self.draw_path()

    # Override
    def draw_path(self):
        path: Sequence[SlidePuzzleState] = self.current_state.get_path()

        path_coords = [self.calculate_center_coords(p) for p in (
            state.get_empty_pos() for state in path)]
        # This line breaks the type checkers, but create_line will flatten the list of tuples..
        self.canvas.create_line(
            path_coords, fill=COLORS[PATH], width=4, tags=PATH)  # type: ignore

    # Override
    def draw_background(self):

        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        # Clear the background grid and tiles
        self.canvas.delete('grid_line')
        self.canvas.delete(TILE)

        # Draw all the "tiles" - really, background color
        self.canvas.create_rectangle(0, 0, w, h, fill=COLORS[TILE], tags=TILE)

        # Creates all vertical lines
        for c in range(0, self.puzzle_dim):
            x = w * c // self.puzzle_dim
            self.canvas.create_line((x, 0, x, h), tags='grid_line', width=3)

        # Creates all horizontal lines
        for r in range(0, self.puzzle_dim):
            y = h * r // self.puzzle_dim
            self.canvas.create_line((0, y, w, y), tags='grid_line', width=3)

    def click_canvas_to_action(self, event) -> SlidePuzzleAction:
        w = self.canvas.winfo_width()  # Get current width of canvas
        col = event.x // (w // self.puzzle_dim)
        h = self.canvas.winfo_height()  # Get current height of canvas
        row = event.y // (h // self.puzzle_dim)
        # print('clicked {}'.format(col))
        return SlidePuzzleAction(row, col)


if __name__ == "__main__":
    if len(argv) > 1:
        file_path = argv[1]
    else:
        initroot = Tk()
        initroot.withdraw()
        file_path = filedialog.askopenfilename(title="Open Slide Puzzle File", initialdir=getcwd(
        ), filetypes=[("SlidePuzzle", ".slidepuzzle"), ("Text", ".txt")])
        initroot.destroy()
    initial_state = SlidePuzzleState.readFromFile(file_path)
    gui = SlidePuzzle_GUI(initial_state, algorithm_names=list(ALGORITHMS.keys(
    )), strategy_names=list(STRATEGIES.keys()), heuristics=SLIDEPUZZLE_HEURISTICS)
    controller = Search_GUI_Controller(
        gui, initial_state, SLIDEPUZZLE_HEURISTICS)
    gui.mainloop()
