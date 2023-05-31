from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, Iterable, NamedTuple, List, Tuple
from copy import deepcopy
from gamesearch_problem import StateNode, Action



"""
An abstract framework for the game of TicTacToe
"""
class TicTacToeAction(NamedTuple, Action):
    """ Represents the playing of a piece in a column.
    Can be created with TicTacToeAction(column).
    """
    row : int
    col : int
    def __str__(self):
        return "Play row {}, col {}".format(self.row, self.col)

    @staticmethod
    def str_to_action(text : str) -> Optional[Action]:
        """Translates a string representing an action 
        (e.g. a user's text input) into an action.
        If the text is not valid, returns None
        """
        try:
            row, col = (int(x) for x in text.split())
            return TicTacToeAction(row, col)
        except ValueError:
            return None


    def action_to_str(self) -> Optional[str]:
        """Translates an action to the most basic string representation
        that should be invertable by str_to_action
        """
        return "{} {}".format(self.row, self.col)

"""
A StateNode representation of the game TicTacToe.
"""
class TicTacToeGameState(StateNode):

    """ Class-level "static" variables"""
    player_names : Tuple[Any,Any] = ("X", "0") 

    action_type : Type[Action] = TicTacToeAction

    num_rows = 3  # board height
    num_cols = 3  # board width
    
    EMPTY = -1

    num_to_symbol = {EMPTY: "_", 0: "X", 1: "0"}
    symbol_to_num = {"_": EMPTY, "X": 0, "0": 1}

    """ Instance Variables """
    board : List[List[int]]

    @staticmethod
    def readFromFile(filename):
        """A 'static' method that reads data from a text file and returns
        a TicTacToeGameState which is an initial state.
        TicTacToe Game file format:
        First line: 1 str for first player name
        Following num_rows lines: num_cols str for pieces or spaces "_" in each row of the board.
        """
        with open(filename, 'r') as file:
            board = []
            first_player = int(TicTacToeGameState.player_names.index(file.readline().strip()))

            for i in range(TicTacToeGameState.num_rows):
                row = [TicTacToeGameState.symbol_to_num[x] for x in file.readline().split()]
                assert(len(row) == TicTacToeGameState.num_cols)
                board.append(row)

        return TicTacToeGameState(
            board = board,
            parent = None,
            depth = 0,
            last_action = None,
            current_player_index = first_player
        )

    @staticmethod
    def defaultInitialState():
        """
        Returns the default initial state (e.g. standard blank board).
        The default is an empty board, player index 0 (player number 1, name "Red")
        """
        return TicTacToeGameState(
            board = [[TicTacToeGameState.EMPTY for c in range(TicTacToeGameState.num_cols)] for r in range(TicTacToeGameState.num_rows)],
            parent = None,
            depth = 0,
            last_action = None,
            current_player_index = 0)


   
    def __init__(self, 
                board : Tuple[int,...],
                parent : Optional[StateNode], 
                last_action: Optional[Action], 
                depth : int, 
                current_player_index : int):
        """
        Creates a game state node.
        Takes:

        board: a 2-d list (list of lists) representing the board.
        Numbers are either 0 (no piece), 1 or 2.

        parent: the preceding TicTacToeGameState along the path taken to reach the state
                (the initial state's parent should be None)
        depth: the number of actions taken in the path to reach the state (aka number of plies)
        last_action: whatever action was last taken to arrive at this state
        current_player_index: the number of the player whose turn it is to take an action

        Use super().__init__() to call this function in the subclass __init__()
        """
        self.board = board
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

        NOTE: In this case,the current player IS implicitly encoded in the features.
        """
        return tuple(tuple(row) for row in self.board)


    def __str__(self) -> str:
        """Return a string representation of the state."""
        ret = ""
        for row in self.board:
            ret += "|".join(TicTacToeGameState.num_to_symbol[piece] for piece in row)
            ret += "\n"
        for i in range(TicTacToeGameState.num_cols * 2 - 1):
            ret += "-"
        ret += "\n"
        ret += "|".join(str(c) for c in range(TicTacToeGameState.num_cols))
        ret += "\n"
        ret += "(P{} [{}]'s turn)\n".format(self.current_player_index, TicTacToeGameState.player_names[self.current_player_index]) 

        return ret

    def endgame_utility(self, player_index : int) -> Optional[float]:
        """Returns the endgame utility of this state from the perspective of the given player.
        If not a terminal (endgame) state, behavior is undefined (but returning None is a good idea)

        For Connect Four, this is simply whether the player has won (+1), lost (-1), or tied (0).
        For Connect Four, the winner is whoever gets
        4 consecutive pieces in a horizontal, vertical, or diagonal direction. A tie occurs if no such
        4 sequence exists, and the board is full
        
        Instead of using this directly, you should incorporate it into an evaluation function.
        The interpretation of this standard utility can be altered by the evaluation function.
        """        
        for player in range(len(TicTacToeGameState.player_names)):
        
            # Horizontal wins
            for r in range(TicTacToeGameState.num_rows):
                if all(self.board[r][c] == player for c in range(TicTacToeGameState.num_cols)) :
                    return 1 if player == player_index else -1

            # Vertical wins
            for c in range(TicTacToeGameState.num_cols):
                if all(self.board[r][c] == player for r in range(TicTacToeGameState.num_rows)) :
                    return 1 if player == player_index else -1

            # Diagonal down-right wins
            if all(self.board[r][c] == player for r, c in zip(range(TicTacToeGameState.num_rows),range(TicTacToeGameState.num_cols))) :
                return 1 if player == player_index else -1

            # Diagonal up-right wins
            if all(self.board[r][c] == player for r, c in zip(reversed(range(TicTacToeGameState.num_rows)),range(TicTacToeGameState.num_cols))) :
                return 1 if player == player_index else -1

        # If you get here, no winner yet!
        return 0

    


    def is_endgame_state(self) -> bool:
        """Returns whether or not this state is an endgame state (terminal)"""
        if len(self.get_all_actions()) == 0:
            return True
        return self.endgame_utility(0) != 0

    def is_legal_action(self, action : TicTacToeAction) -> bool:
        """Returns whether an action is legal from the current state"""
        if action.col not in range(TicTacToeGameState.num_cols) or action.row not in range(TicTacToeGameState.num_rows) :
            return False
        
        return self.board[action.row][action.col] == TicTacToeGameState.EMPTY


    def get_all_actions(self) -> Iterable[TicTacToeAction]:
        """
        Return all legal actions from this state. Actions may be whatever type you wish.
        Note that the ordering may matter for the algorithm (e.g. Alpha-Beta pruning).
        """
        actions = []
        for row in range(TicTacToeGameState.num_rows):
            for col in range(TicTacToeGameState.num_cols):
                if self.get_piece_at(row,col) == TicTacToeGameState.EMPTY:
                    actions.append(TicTacToeAction(row,col))
        return actions


    def get_next_state(self, action : TicTacToeAction) -> StateNode:
        """ Return a new StateNode that represents the state that results from taking the given action from this state.
        The new StateNode object should have this StateNode (self) as its parent, and action as its last_action.

        -- action is assumed legal (is_legal_action called before), but a ValueError may be passed for illegal actions if desired.
        """

        new_board = deepcopy(self.board)
        new_board[action.row][action.col] = self.current_player_index

        return TicTacToeGameState(board = new_board,
            parent = self,
            depth = self.depth + 1,
            last_action = action,
            current_player_index = (self.current_player_index + 1) % len(TicTacToeGameState.player_names) )


    """ Additional TicTacToe specific methods """

    def get_piece_at(self, row, col) -> int:
        return self.board[row][col]
