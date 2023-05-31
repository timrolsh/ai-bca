from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, Iterable, NamedTuple, List, Tuple
from copy import copy

from gamesearch_problem import StateNode, Action

"""
An abstract framework for the game of Nim.
The default utility is based on the misere variation of the game - the losing condition is taking the last stone.
"""

class NimAction(NamedTuple, Action):
    """ Represents the taking of some number of stones from a pile.
    Can be created with NimAction(stones, pile).
    Properties stones and pile can be accessed with dot notation or as if a tuple (r,c)
    """
    stones : int
    pile : int

    def __str__(self):
        return "{} stones from pile {}".format(self.stones, self.pile)

    @staticmethod
    def str_to_action(text : str) -> Optional[Action]:
        """Translates a string representing an action 
        (e.g. a user's text input) into an action.
        If the text is not valid, returns None
        """
        try:
            stones, pile = (int(x) for x in text.split())
            return NimAction(stones, pile)
        except ValueError:
            return None

    
    def action_to_str(self) -> Optional[str]:
        """Translates an action to the most basic string representation
        that should be invertable by str_to_action
        """
        return "{} {}".format(self.stones, self.pile)

class NimGameState(StateNode):
    """ An abstract object that represents a a state in the game Nim. 
    
    It also serves as a search tree "node" which includes information about the state's
    parent, last action taken (that leads to this state), and the length/cost of the path
    that led to this state.
    """

    """ Class-level "static" variables"""
    player_names : Tuple[Any,Any] = ("A","B")
    action_type : Type[Action] = NimAction
    move_limits : Optional[Tuple[int,...]] = None
    
    # Instance variables
    parent : StateNode
    last_action : Action
    depth : int
    current_player_index : int # index of the current player in player_names


    @staticmethod
    def readFromFile(filename : str) -> StateNode:
        """ Nim Game file format:
        First line: 1 int for number of piles, followed by a list of valid numbers of stones you may remove on a turn.
            If only the number of piles, any amount is legal.
        Following lines: 1 int for initial number of stones in the pile
        """
        with open(filename, 'r') as file:
            first_line = [int(x) for x in file.readline().split()]
            num_rows = first_line[0]
            NimGameState.move_limits = tuple(first_line[1:]) if len(first_line) > 1 else None

            board = tuple(int(file.readline()) for i in range(num_rows))

        return NimGameState(
            board = board,
            parent = None,
            depth = 0,
            last_action = None,
            current_player_index = 0)


    @staticmethod
    def defaultInitialState() -> StateNode:
        """
        Returns the default initial state (e.g. standard blank board).
        The default is 3 piles of 3,4,5, and no move limits
        """
        return NimGameState(
            board = (3,4,5),
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
        
        """Creates a StateNode that represents a state of the game and context for how the agent gets 
        to this state (the path, aka a series of state-action transitions).
        
        Keyword Arguments:
        parent -- the preceding StateNode along the path to reach this state. None, for an initial state.
        last_action -- the preceding action taken along the path to reach this state. None, for an initial state. 
        depth -- the number of actions taken in the path to reach the state from the root of the tree (aka level or ply)
        current_player_index: the number of the player whose turn it is to take an action

        In any subclass of StateNode, the __init__() should take additional parameters that help define its state features.
        Use super.__init__() to call this function and pass appropriate parameters.
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

        NOTE: Different current players DOES mean the state is different.
        The current player might be implicitly encoded in other features, but if not it should be explicitly included.
        """
        return self.board, self.current_player_index

    def __str__(self) -> str:
        """Return a string representation of the state."""
        ret = ""
        for pile, stones in enumerate(self.board):
            ret += str(pile) + "|" + "*" * stones + "\n"
        ret += "(P{} [{}]'s turn)\n".format(self.current_player_index, NimGameState.player_names[self.current_player_index]) 
        return ret

    def is_endgame_state(self) -> bool:
        """Returns whether or not this state is an endgame state (terminal)"""
        return all(pile == 0 for pile in self.board)

    def endgame_utility(self, player_index : int) -> Optional[float]:
        """Returns the endgame utility of this state from the perspective of the given player.
        If not a terminal (endgame) state, behavior is undefined (but returning None is a good idea)

        For Nim, this is simply whether the player has won (+1), lost (-1), or tied (0).
        In this variation of Nim, the player who takes the last stone is the loser

        Instead of using this directly, you should incorporate it into an evaluation function.
        The interpretation of this standard utility can be altered by the evaluation function.
        """
        # The last player to play took the last stone.
        if self.parent.current_player_index == player_index:
            return -1
        else: # If that's not you, you won!
            return 1

    def is_legal_action(self, action : NimAction) -> bool:
        """Returns whether an action is legal from the current state"""
        return ((NimGameState.move_limits == None or action.stones in NimGameState.move_limits) 
                and (action.pile >= 0 and action.pile < len(self.board))
                and (self.board[action.pile] >= action.stones and action.stones > 0)) 
        
    def get_all_actions(self) -> Iterable[NimAction]:
        """
        Return all legal actions from this state. Actions may be whatever type you wish.
        Note that the ordering may matter for the algorithm (e.g. Alpha-Beta pruning).
        """
        actions = []
        for pile, max_stones in enumerate(self.board):
            for stones in range(1,max_stones+1):
                if NimGameState.move_limits == None or stones in NimGameState.move_limits:
                    actions.append(NimAction(stones, pile))

        return actions


    def get_next_state(self, action : NimAction) -> StateNode:
        """ Return a new StateNode that represents the state that results from taking the given action from this state.
        The new StateNode object should have this StateNode (self) as its parent, and action as its last_action.

        -- action is assumed legal (is_legal_action called before), but a ValueError may be passed for illegal actions if desired.
        """
        nb = list(self.board)
        nb[action.pile] -= action.stones
        return NimGameState(board = tuple(nb),
            parent = self,
            depth = self.depth + 1,
            last_action = action,
            current_player_index = (self.current_player_index + 1) % len(NimGameState.player_names) )
        

    """ Additional Nim specific methods, useful for writing heuristic function """

    def get_stones_in_pile(self, pile : int) -> int:
        return self.board[pile]

    def get_num_piles(self) -> int:
        return len(self.board)