from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, Iterable, NamedTuple, List, Tuple, TypeVar
from copy import deepcopy
from gamesearch_problem import StateNode, Action

Terrain = TypeVar('Terrain', bound=str)


FLOOR : Terrain = '.'
WALL : Terrain = '#'
CLEANED : Terrain = '%'

"""
An abstract framework for the game of RoombaRace, based on the 
Tron light-bike game. Any spot previously traversed by either agent (CLEANED) 
cannot be traversed again. The goal is to trap your opponent so they cannot move.

"""

class Coordinate(NamedTuple):
    """ Represents a specific location on the grid with given row r and column c
    Can be created with Coordinate(r=row, c=col), or just Coordinate(row,col).
    Properties r and c can be accessed with dot notation or as if a tuple (r,c)
    """
    r : int
    c : int

STR_TO_ACTIONS : Dict[str, Coordinate] = { "N": Coordinate(-1,0), "E": Coordinate(0,1), "S": Coordinate(1,0), "W": Coordinate(0, -1)}
NEIGHBORING_STEPS : Dict[Coordinate, str] = {Coordinate(-1,0): "North", Coordinate(0,1): "East", Coordinate(1,0): "South", Coordinate(0, -1): "West"}


class RoombaRaceAction(Coordinate, Action):
    """ Representing the *relative* coordinate a Roomba is trying to move to - that is, the 
    number of rows down and columns right the roomba is trying to move from its current position. """
    def __str__(self):
        return NEIGHBORING_STEPS[self]

    @staticmethod
    def str_to_action(text : str) -> Optional[Action]:
        """Translates a string representing an action 
        (e.g. a user's text input) into an action.
        If the text is not valid, returns None
        """
        try:
            return STR_TO_ACTIONS[text.upper()[0]]
        except KeyError:
            return None


"""
A StateNode representation of the game RoombaRace.
"""
class RoombaRaceGameState(StateNode):


    """ Class-level "static" variables"""
    player_names : Tuple[Any, Any] = ("R","B")
    action_type : Type[Action] = RoombaRaceAction


    """ Instance Variables """
    grid : List[List[Terrain]]
    positions : List[Coordinate]

    """
    A 'static' method that reads data from a text file and returns
    a RoombaGameState which is an initial state.
    """
    @staticmethod
    def readFromFile(filename):
        """ RoombaRace Game file format:
        First line: 2 ints for num_rows and num_cols
        Line 1: 2 ints for coordinate (row, col) of player 0 ('Red')
        Line 2: 2 ints for coordinate (row, col) of player 1 ('Blue')
        Following num_rows lines: num_cols-length str with chars as Terrain for board.
        """
        with open(filename, 'r') as file:
            grid = []
            num_rows, num_cols = [int(x) for x in file.readline().split()]
            init_r_1, init_c_1 = [int(x) for x in file.readline().split()]
            init_r_2, init_c_2 = [int(x) for x in file.readline().split()]
            for i in range(num_rows):
                row = list(file.readline().strip()) # or file.readline().split()
                assert (len(row) == num_cols)
                grid.append(row) 
            # grid is a list of lists - a 2d grid!

        return RoombaRaceGameState(positions = [Coordinate(init_r_1, init_c_1),Coordinate(init_r_2, init_c_2)],
                            grid = grid,
                            parent = None,
                            depth = 0,
                            last_action = None,
                            current_player_index = 0)

    """
    A 'static' method that creates some default
    RoombaGameState which is an initial state (e.g. standard blank board).
    """
    @staticmethod
    def defaultInitialState() -> StateNode:
        """
        Returns the default initial state (e.g. standard blank board).
        The default is an empty board, player index 0 (player number 1, name "Red")
        """
        return RoombaRaceGameState(positions = [(2, 1),(2, 5)],
                            grid =  [[ FLOOR for c in range(7)] for r in range(5)],
                            parent = None,
                            depth = 0,
                            last_action = None,
                            current_player_index = 0)


   
    def __init__(self, 
                positions : List[Coordinate],
                grid : List[List[Terrain]],
                parent : Optional[RoombaRaceGameState], 
                last_action: Optional[Action], 
                depth : int, 
                current_player_index : int):
        """
        Creates a game state node.
        Takes:

        positions: a list of Coordinates representing the positions of the players.
        grid: a list of lists representing a grid of Terrain objects, the current status of the environment

        parent: the preceding RoombaGameState along the path taken to reach the state
                (the initial state's parent should be None)
        depth: the number of actions taken in the path to reach the state (aka number of plies)
        last_action: whatever action was last taken to arrive at this state
        current_player_index: the number of the player whose turn it is to take an action

        Use super().__init__() to call this function in the subclass __init__()
        """
        self.positions = positions
        self.grid = grid
        super().__init__(parent=parent,
            last_action=last_action,
            depth=depth,
            current_player_index=current_player_index)

    
    def get_state_features(self) -> Hashable:
        """Returns a fully featured representation of the state.

        This should return something consistent, immutable, and hashable - 
        generally, tuples of primitives, strings, or other tuples (generally no lists or objects).

        If two StateNode objects represent the same state, get_state_features() should return the same for both objects.
        However, two StateNodes with identical state features may not represent the same node of the search tree -
        that is, they may have different parents, last actions, depths etc...

        In the case of RoombaRaceGameState, the features are the positions of the Roombas and the state of the grid.

        NOTE: In this case,the current player IS implicitly encoded in the features.
        """
        return (tuple(tuple(pos) for pos in self.positions), tuple(tuple(row) for row in self.grid) )


    def __str__(self) -> str:
        """Return a string representation of the state."""
        s = "\n".join(["".join(row) for row in self.grid])
        for i,p in enumerate(RoombaRaceGameState.player_names):
            r,c = self.get_position(i)
            str_pos =  r * (self.get_width()+1) + c
            s = s[:str_pos] + str(p)[0] + s[str_pos+1:] + "\n"
        s += "(P{} [{}]'s turn)\n".format(self.current_player_index, RoombaRaceGameState.player_names[self.current_player_index]) 

        return s



    def is_endgame_state(self) -> bool:
        """Returns whether or not this state is an endgame state (terminal)"""
        return len(self.get_all_actions()) == 0


    def endgame_utility(self, player_index : int) -> Optional[float]:
        """Returns the endgame utility of this state from the perspective of the given player.
        If not a terminal (endgame) state, behavior is undefined (but returning None is a good idea)

        For Roomba Race, this is simply whether the player has won (+1) or lost (-1).
        For Roomba Race, the loser is the first person to find themselves without available movement 
        options. 
        
        Instead of using this directly, you should incorporate it into an evaluation function.
        The interpretation of this standard utility can be altered by the evaluation function.
        """ 
        return 1 if self.current_player_index != player_index else -1 

    def is_legal_action(self, action : Coordinate) -> bool:
        """Returns whether an action is legal from the current state"""
        if action not in NEIGHBORING_STEPS:
            return False
        my_r, my_c = self.get_position(self.current_player_index)
        new_pos = Coordinate(my_r + action.r, my_c + action.c)
        # Don't use any out-of-bounds moves
        # Don't allow moving to anything but (unclean) floor
        # No moving to other player positions

        return (self.is_inbounds(new_pos) 
                and self.get_terrain(new_pos) == FLOOR 
                and new_pos not in self.positions)


    def get_all_actions(self) -> Iterable[RoombaRaceAction]:
        """
        Return all legal actions from this state. Actions may be whatever type you wish.
        Note that the ordering may matter for the algorithm (e.g. Alpha-Beta pruning).
        """
        return  [RoombaRaceAction(*a) for a in NEIGHBORING_STEPS if self.is_legal_action(a)] 



    def get_next_state(self, action : RoombaRaceAction) -> RoombaRaceGameState:
        """ Return a new StateNode that represents the state that results from taking the given action from this state.
        The new StateNode object should have this StateNode (self) as its parent, and action as its last_action.

        -- action is assumed legal (is_legal_action called before), but a ValueError may be passed for illegal actions if desired.
        """
        new_grid = deepcopy(self.grid)

        dr, dc = action
        my_r, my_c = self.get_position(self.current_player_index)
        new_r, new_c = my_r + dr, my_c + dc

        new_grid[my_r][my_c] = CLEANED

        new_positions = deepcopy(self.positions)
        new_positions[self.current_player_index] = (new_r, new_c)
        
        return RoombaRaceGameState (
            positions = new_positions,
            grid = new_grid,
            parent = self,
            depth = self.depth + 1,
            last_action = action,
            current_player_index = (self.current_player_index + 1) % len(RoombaRaceGameState.player_names) 
        )


    """ Additional RoombaRace specific methods, useful for writing heuristic function """



    def get_width(self) -> int:
        """Returns the width (number of cols) of the maze"""
        return len(self.grid[0])


    def get_height(self) -> int:
        """Returns the height (number of rows) of the maze"""
        return len(self.grid)

    
    def get_grid(self) -> List[List[Terrain]]:
        """ Returns a 2d-list grid of the maze. """
        return self.grid

    def is_inbounds(self, coord : Coordinate) -> bool:
        """ Returns True if coord is within the valid bounds of the grid. """
        return (coord.r >= 0) and (coord.c  >= 0) and (coord.r < self.get_height()) and (coord.c < self.get_width())

    def get_position(self, player_index : int) -> Coordinate:
        """Returns a 2-tuple of a player roomba's position (row, col) in the maze"""
        return self.positions[player_index]

    def get_terrain(self, coord : Coordinate) -> Terrain:
        """ Return the kind of terrain at coord """
        return self.grid[coord.r][coord.c]


