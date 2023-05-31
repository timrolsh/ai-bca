from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, Iterable, NamedTuple, List, Tuple
from copy import deepcopy
from gamesearch_problem import StateNode, Action



"""
An abstract framework for the game of ConnectFour
"""
class ConnectFourAction(NamedTuple, Action):
    """ Represents the playing of a piece in a column.
    Can be created with ConnectFourAction(column).
    """
    column : int

    def __str__(self):
        return "Play column {}".format(self.column)

    @staticmethod
    def str_to_action(text : str) -> Optional[Action]:
        """Translates a string representing an action 
        (e.g. a user's text input) into an action.
        If the text is not valid, returns None
        """
        try:
            return int(text)
        except ValueError:
            return None

    
    def action_to_str(self) -> Optional[str]:
        """Translates an action to the most basic string representation
        that should be invertable by str_to_action
        """
        return str(self.column)

"""
A StateNode representation of the game Connect Four.
"""
class ConnectFourGameState(StateNode):


    """ Class-level "static" variables"""
    player_names : Tuple[Any,Any] = ("X", "0") 
    action_type : Type[Action] = ConnectFourAction

    num_rows = 6  # board height
    num_cols = 7  # board width

    EMPTY = -1

    num_to_symbol = {EMPTY: "_", 0: "X", 1: "0"}
    symbol_to_num = {"_": EMPTY, "X": 0, "0": 1}


    """ Instance Variables """
    board : List[List[int]]


    @staticmethod
    def readFromFile(filename):
        """A 'static' method that reads data from a text file and returns
        a ConnectFourGameState which is an initial state.
        Connect Four Game file format:
        First line: 1 int for symbol of first player 
        Following num_rows lines: num_cols str for symbols or spaces "_" in each row of the board.
        """
        with open(filename, 'r') as file:
            board = []
            first_player = int(ConnectFourGameState.player_names.index(file.readline().strip()))

            for i in range(ConnectFourGameState.num_rows):
                row = [ConnectFourGameState.symbol_to_num[x] for x in file.readline().split()]
                assert(len(row) == ConnectFourGameState.num_cols)
                board.append(row)

        return ConnectFourGameState(
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
        return ConnectFourGameState(
            board = [[ConnectFourGameState.EMPTY for c in range(ConnectFourGameState.num_cols)] for r in range(ConnectFourGameState.num_rows)],
            parent = None,
            depth = 0,
            last_action = None,
            current_player_index = 0)


   
    def __init__(self, 
                board : List[List[int]],
                parent : Optional[StateNode], 
                last_action: Optional[Action], 
                depth : int, 
                current_player_index : int):
        """
        Creates a game state node.
        Takes:

        board: a 2-d list (list of lists) representing the board.
        Numbers are either -1 (no piece), or the index of the player's piece.

        parent: the preceding ConnectFourGameState along the path taken to reach the state
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
            ret += "|".join(ConnectFourGameState.num_to_symbol[piece] for piece in row)
            ret += "\n"
        for i in range(ConnectFourGameState.num_cols * 2 - 1):
            ret += "-"
        ret += "\n"
        ret += "|".join(str(c) for c in range(ConnectFourGameState.num_cols))
        ret += "\n"

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
        for player in range(len(ConnectFourGameState.player_names)):
            if self.get_num_chains(4, player):
                return 1 if player == player_index else -1
        return 0

    


    def is_endgame_state(self) -> bool:
        """Returns whether or not this state is an endgame state (terminal)"""
        if len(self.get_all_actions()) == 0:
            return True
        return self.endgame_utility(0) != 0

    def is_legal_action(self, action : ConnectFourAction) -> bool:
        """Returns whether an action is legal from the current state"""
        return (action.column in range(ConnectFourGameState.num_cols)) and not self.is_column_full(action.column)
        

    def get_all_actions(self) -> Iterable[ConnectFourAction]:
        """
        Return all legal actions from this state. Actions may be whatever type you wish.
        Note that the ordering may matter for the algorithm (e.g. Alpha-Beta pruning).
        """
        return [ConnectFourAction(col) for col in range(ConnectFourGameState.num_cols)
                    if not self.is_column_full(col) ]


    def get_next_state(self, action : ConnectFourAction) -> StateNode:
        """ Return a new StateNode that represents the state that results from taking the given action from this state.
        The new StateNode object should have this StateNode (self) as its parent, and action as its last_action.

        -- action is assumed legal (is_legal_action called before), but a ValueError may be passed for illegal actions if desired.
        """

        r = ConnectFourGameState.num_rows - self.get_column_height(action.column) - 1

        new_board = deepcopy(self.board)
        new_board[r][action.column] = self.current_player_index

        return ConnectFourGameState(board = new_board,
            parent = self,
            depth = self.depth + 1,
            last_action = action,
            current_player_index = (self.current_player_index + 1) % len(ConnectFourGameState.player_names) )


    """ Additional ConnectFour specific methods, useful for writing heuristic functions """

    """Return the number of pieces in the column; e.g., 0 if the column is empty."""
    def get_column_height(self, col_number : int):
        height = 0
        for row in reversed(self.board) :
            if row[col_number] != ConnectFourGameState.EMPTY:
                height += 1
            else :
                break
        return height

    """Return True if column is full, False otherwise. Just checks the top row for speed."""
    def is_column_full(self, col_number : int) :
        return self.board[0][col_number] != ConnectFourGameState.EMPTY

    def get_piece_at(self, row :int , col :int):
        return self.board[row][col]

    def get_num_chains(self, chain_len : int, player_piece : int):
        if chain_len > 1:
            return (self.get_num_chains_hor(chain_len, player_piece) +
                self.get_num_chains_ver(chain_len, player_piece) +
                self.get_num_chains_diag(chain_len, player_piece) )
        else : # if len 1, don't repeat count
                return self.get_num_chains_hor(chain_len, player_piece)
                
    def get_num_chains_hor(self, chain_len : int, player_piece : int):
        count = 0
        # Horizontal chains
        # Each leftmost position of a horizontal 4 sequence
        for r in range(ConnectFourGameState.num_rows):
            for c in range(ConnectFourGameState.num_cols - chain_len + 1):
                # check 4 consecutive rightwards all same as player_piece
                if all(self.board[r][c+i] == player_piece for i in range(0, chain_len)) :
                    count += 1

        return count

    def get_num_chains_ver(self, chain_len : int, player_piece : int):
        count = 0
        # Vertical chains
        # Each uppermost position of a vertical 4 sequence
        for c in range(ConnectFourGameState.num_cols):
            for r in range(ConnectFourGameState.num_rows - chain_len + 1):
                # check 4 consecutive in diagonal down-right all same as player_piece
                if all(self.board[r+i][c] == player_piece for i in range(0, chain_len)) :
                    count += 1

        return count

    def get_num_chains_diag(self, chain_len : int, player_piece : int):
        count = 0

        # Diagonal down-right chains
        # Each leftmost position of a diagonal down 4 sequence
        for r in range(ConnectFourGameState.num_rows - chain_len + 1):
            for c in range(ConnectFourGameState.num_cols - chain_len + 1):
                # check 4 consecutive in digonal down-right same as leftmost player_piece
                if all(self.board[r+i][c+i] == player_piece for i in range(0, chain_len)) :
                    count += 1

        # Diagonal up-right chains
        # Each leftmost position of a diagonal up-right 4 sequence
        for r in range(chain_len - 1, ConnectFourGameState.num_rows):
            for c in range(ConnectFourGameState.num_cols - chain_len + 1):
                # check 4 consecutive in diagonal up-right direction all same as player_piece
                if all(self.board[r-i][c+i] == player_piece for i in range(0, chain_len)) :
                    count += 1

        return count
