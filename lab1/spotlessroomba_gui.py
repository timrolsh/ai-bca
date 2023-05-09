# Timothy Rolshud and Krish Arora

from __future__ import annotations
from typing import *
from tkinter import filedialog, Tk
from os import getcwd
from sys import argv
from spotlessroomba_problem import *
from spotlessroomba_heuristics import SPOTLESSROOMBA_HEURISTICS
from search_algorithms import ALGORITHMS, STRATEGIES
from roomba_gui import *
from search_gui import Search_GUI_Controller

# State visualization too big? Change these numbers
MAX_HEIGHT = 350
MAX_WIDTH = 450

TEXT = 'text'
COLORS[TEXT] = 'black'


class SpotlessRoomba_GUI(Roomba_GUI):

    current_state: SpotlessRoombaState

    def __init__(self, initial_state: SpotlessRoombaState, algorithm_names: Sequence[str], strategy_names: Sequence[str], heuristics: Dict[str, Callable[[StateNode], float]]):
        super().__init__(initial_state=initial_state, algorithm_names=algorithm_names,
                         strategy_names=strategy_names, heuristics=heuristics)
        self.title("Spotless Roomba Search Visualizer")

        # Override
    def draw_state(self):
        self.canvas.delete(AGENT)
        self.canvas.delete('dirt')

        # roomba agent
        x1, y1, x2, y2 = self.calculate_box_coords(self.current_state.position)
        # self.canvas.create_oval(x1, y1, x2, y2, fill= '', outline = COLORS[SEEN], tag= SEEN)
        self.canvas.create_oval(x1, y1, x2, y2, fill=COLORS[AGENT], tags=AGENT)

        # Draw remaining dirt
        maze = self.current_state.grid
        for coord in self.current_state.dirty_locations:
            self.canvas.create_rectangle(*self.calculate_box_coords(
                coord), fill=COLORS[DIRTY_TERRAIN[maze[coord.row][coord.col]]], tags='dirt')

        self.canvas.delete(PATH)
        self.canvas.delete(START)
        self.canvas.delete(TEXT)
        if self.current_state.depth > 0:
            self.draw_path()
        else:
            self.canvas.delete(SEEN)  # This is a bit of a hack...

    # Override
    def draw_path(self):
        path: Sequence[SpotlessRoombaState] = cast(
            Sequence[SpotlessRoombaState], self.current_state.get_path())
        path_coords = [self.calculate_center_coords(state.position)
                       for state in path]
        # This line breaks the type checkers, but create_line will flatten the list of tuples..
        self.canvas.create_line(
            path_coords, fill=COLORS[PATH], width=3, tags=PATH, )  # type: ignore

        # Draw outline of initial roomba position at the start of the path
        self.canvas.create_oval(self.calculate_box_coords(
            path[0].position), fill='', outline=COLORS[START], tags=START)

        # Draw numbers on cleaned up spots.
        dirt_count = 1
        text_size = self.canvas.winfo_height() // (self.height * 2)
        for state, coord in zip(path[1:], path_coords[1:]):
            if state.parent is not None and state.position in state.parent.dirty_locations:
                self.canvas.create_text(coord, fill=COLORS[TEXT], tags=TEXT,
                                        text=str(dirt_count), font=('Times New Roman', text_size, 'bold'))
                dirt_count += 1


if __name__ == "__main__":
    if len(argv) > 1:
        file_path = argv[1]
    else:
        initroot = Tk()
        initroot.withdraw()
        file_path = filedialog.askopenfilename(title="Open Roomba File", initialdir=getcwd(
        ), filetypes=[("Roomba", ".roomba"), ("Text", ".txt")])
        initroot.destroy()
    initial_state = SpotlessRoombaState.readFromFile(file_path)
    gui = SpotlessRoomba_GUI(initial_state, algorithm_names=list(ALGORITHMS.keys(
    )), strategy_names=list(STRATEGIES.keys()), heuristics=SPOTLESSROOMBA_HEURISTICS)
    controller = Search_GUI_Controller(
        gui, initial_state, SPOTLESSROOMBA_HEURISTICS)
    gui.mainloop()
