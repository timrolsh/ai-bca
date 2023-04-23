# Lab 1, Part 1b: Problem Representation.
# Name(s): Tim Rolshud, Krish Arora

from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, Iterable, Dict, Union, List, Tuple, cast

from search_problem import StateNode, Action

#### Lab 1, Part 1b: Problem Representation #################################################


class Coordinate:
    """ Represents a specific location on the grid with given row and col(umn)
    The first row and column are numbered 0.
    """
    row: int
    col: int

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    # Override
    def __str__(self):
        return "(R:{}, C:{})".format(self.row, self.col)

    # Override
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.row == other.row and self.col == other.col

    # Override
    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def sameAs(self, r: int, c: int) -> bool:
        """Convenience method for checking equivalence to a coordinate pair"""
        return self.row == r and self.col == c


class SlidePuzzleAction(Coordinate, Action):
    """Represents the coordinate of the tile that is to be moved into 
    the empty space.

    Subclass of both Coordinate and Action
    """
    pass


class SlidePuzzleState(StateNode):
    """ A state node for the slide puzzle environment. """

    # Type Hints allow for the optional type declaration of "instance variables" this way, like Java.
    tiles: Tuple[Tuple[int, ...], ...]
    empty_pos: Coordinate
    # These are already mentioned in the StateNode superclass, but more specifically typed here
    parent: Optional[SlidePuzzleState]
    last_action: Optional[SlidePuzzleAction]

    @staticmethod
    def readFromFile(filename: str) -> SlidePuzzleState:
        """Reads data from a text file and returns a SlidePuzzleState which is an initial state.
        The file format is simple: the first line has a number, which is the N, 
        the # of rows/columns of the puzzle (all puzzles are square). 
        There are then N lines with N numbers (space delimited), 
        representing the initial configuration of the tiles in the grid. 
        The number 0 represents the blank tile. 
        """
        with open(filename, 'r') as file:
            # read file and return an initial SlidePuzzleState

            data = file.read().splitlines()
            n = int(data[0])
            tiles = []
            for i in range(1, n + 1):
                tiles.append(tuple(int(x) for x in data[i].split()))
            tiles = tuple(tiles)
            empty_pos = Coordinate(0, 0)
            for i in range(n):
                for j in range(n):
                    if tiles[i][j] == 0:
                        empty_pos = Coordinate(i, j)

            return SlidePuzzleState(
                tiles=tiles,
                empty_pos=empty_pos,
                parent=None,
                last_action=None,
                depth=0,
                path_cost=0,
            )

    # Override
    def __init__(self,
                 tiles: Tuple[Tuple[int, ...], ...],
                 empty_pos: Coordinate,
                 parent: Optional[SlidePuzzleState],
                 last_action: Optional[SlidePuzzleAction],
                 depth: int,
                 path_cost: float = 0.0):
        """Creates a SlidePuzzleState that represents a state of the environment and context for how the agent gets 
        to this state (the path, aka a series of state-action transitions).

        Keyword Arguments:
        All the arguments for StateNode's __init__; Use super.__init__() to call this function and pass appropriate parameters.
        tiles -- a tuple grid of integers representing the position of different numbered tiles
        empty_pos -- a coordinate indicating the position of the empty spot (tile 0)
        """
        super().__init__(parent=parent, last_action=last_action,
                         depth=depth, path_cost=path_cost)
        self.tiles = tiles
        self.empty_pos = empty_pos

    """ Additional accessor methods - needed for the GUI"""

    def get_size(self) -> int:
        """Returns the dimension N of the square puzzle represented which is N-by-N."""
        return len(self.tiles)

    def get_tile_at(self, coord: Coordinate) -> int:
        """ Returns the number of the tile at the given Coordinate.
        If the position is empty, return 0.
        Ideally, this should be done in constant time, not O(N) or O(N^2) time...
        """
        return self.tiles[coord.row][coord.col]

    def get_empty_pos(self) -> Coordinate:
        """Returns Coordinate of the empty tile.
        Ideally, this should be done in constant time, not O(N) or O(N^2) time...
        """
        return self.empty_pos

    """ Overridden methods from StateNode """

    # Override
    def get_state_features(self) -> Hashable:
        """Returns a full featured representation of the state. 

        In the case of the slide puzzle, the current positions of all the tiles are the features.

        If two SlidePuzzleState objects represent the same state, get_features() should return the same for both objects.
        However, two SlidePuzzleState with identical state features may not represent the same node of the search tree -
        that is, they may have different parents, last actions, path lengths/costs etc...
        """
        return self.tiles

    # Override

    def __str__(self) -> str:
        """Return a string representation of the state.

           This should return N lines of N numbers each, separated by whitespace,
           similar to the file format for initial states
        """
        n = self.get_size()
        return "\n".join(" ".join("{:2d}".format(self.tiles[r][c]) for c in range(n)) for r in range(n))

    # Override
    def is_goal_state(self) -> bool:
        """Returns if a goal (terminal) state. 
        The goal of the slide puzzle is to have the empty spot in the 0th row and 0th col,
        and then the rest of the numbered tiles in order down the rows!
        """
        size = self.get_size()
        for r in range(size):
            for c in range(size):
                if r == 0 and c == 0:
                    if self.tiles[r][c] != 0:
                        return False
                else:
                    if self.tiles[r][c] != r * size + c:
                        return False
        return True

    # Override
    def is_legal_action(self, action: SlidePuzzleAction) -> bool:
        """Returns whether an action is legal from the current state

        Actions in the slide puzzle environment involve moving a tile into
        the adjacent empty spot.

        Actions are Coordinate objects, specifying the position of the tile that
        is to be moved into the empty slot. That Coordinate needs to be not out of bounds, and 
        actually adjacent to the empty slot.
        """
        in_valid_row = 0 <= action.row < self.get_size()
        in_valid_col = 0 <= action.col < self.get_size()
        is_adjacent = abs(action.row - self.empty_pos.row) + abs(action.col - self.empty_pos.col) == 1
        return in_valid_row and in_valid_col and is_adjacent

    # Override

    def get_all_actions(self) -> Iterable[SlidePuzzleAction]:
        """Return all legal actions at this state."""
        # return a list, tuple, or use comprehension
        return [
            Coordinate(r, c)
            for r in range(self.get_size())
            for c in range(self.get_size())
            if self.is_legal_action(Coordinate(r, c))
        ]
    # Override

    def describe_last_action(self) -> str:
        """Returns a string describing the last_action taken (that resulted in transitioning from parent to this state)
        (Can be None or "None" if the initial state)

        The action should be described as "Moved tile X" where X is the tile number
        that last got slid into the empty spot.
        """
        if self.parent is None or self.last_action is None:
            return "No Action Yet"
        else:
            return "Moved tile {}".format(self.parent.get_tile_at(self.last_action))

    # Override
    def get_next_state(self, action: SlidePuzzleAction) -> SlidePuzzleState:
        """ Return a new StateNode that represents the state that results from taking the given action from this state.
        The new StateNode object should have this StateNode (self) as its parent, and action as its last_action.

        -- action is assumed legal (is_legal_action called before), but a ValueError may be passed for illegal actions if desired.
        """
        size = self.get_size()
        new_tiles = [[0] * size for _ in range(size)]
        for r in range(size):
            for c in range(size):
                new_tiles[r][c] = self.tiles[r][c]
        
        new_tiles[self.empty_pos.row][self.empty_pos.col] = self.tiles[action.row][action.col]
        new_tiles[action.row][action.col] = 0
        
        return SlidePuzzleState(
            tiles=tuple(tuple(row) for row in new_tiles),
            empty_pos=action,
            parent=self,
            last_action=action,
            depth=self.depth + 1,
            path_cost=self.path_cost + 1,
        )

    """ You may add additional methods that may be useful! """
