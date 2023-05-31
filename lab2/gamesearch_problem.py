from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, List, Tuple, Callable
from copy import copy
import random

"""
An abstract framework for a 2-agent purely adversarial utility search problem, aka a 2-player zero-sum game.

The Action and StateNode classes are not meant to be instantiated or used directly.
Rather, they serve as an abstract superclasses for different environment/problem representations.

Your game tree search algorithms will work with StateNode objects, making them generalizable
for all kinds of problems.

############################################################################################################
You should notice that this is extremely similar to the StateNode back in search_problem.py for the last lab. 
The differences are:

Action:
- str_to_action(text) method that converts a str to an Action

StateNode
- No path cost instance variable
- current_player_index instance variable
- defaultInitialState() method that yields a standard "starting board"
- get_all_actions() returns a List, specifically (not a general Iterable)
- is_endgame_state(), instead of is_goal_state()
- endgame_utility(player_index) method, which returns endgame utilities
"""

class Action:
    """ An abstract object that represents an action in an environment """
    def __str__(self) -> str:
        """ Returns a string that describes this action """
        raise NotImplementedError
    
    def __eq__(self, other) -> bool:
        """ Returns whether other is equivalent in value """
        if not isinstance(other, type(self)) :
            return False
        return NotImplementedError

    @staticmethod
    def str_to_action(text : str) -> Optional[Action]:
        """Translates a string representing an action 
        (e.g. a user's text input) into an action.
        This should be essentially the inverse of action_to_str
        
        If the text is not valid, returns None

        Should be implemented by subclasses.
        """
        raise NotImplementedError

    
    def action_to_str(self) -> Optional[str]:
        """Translates an action to the most basic string representation
        that should be invertable by str_to_action

        Could be overridden
        """
        return str(self)

class StateNode:
    """ An abstract object that represents a a state in an environment. 
    
    It also serves as a search tree "node" which includes information about the state's
    parent, last action taken (that leads to this state), and the length/cost of the path
    that led to this state.
    """

    """ Class-level "static" variables, accessible by all subclasses.
        Should be overridden by subclasses. 
    """
    player_names : Tuple[Any,Any] = ("P1","P2") 
    action_type : Type[Action] = Action

    # Type Hints allow for the optional type declaration of instance variables, like Java
    parent : StateNode
    last_action : Action
    depth : int
    current_player_index : int # index of the current player in player_names. Either 0 or 1

    @staticmethod
    def readFromFile(filename : str) -> StateNode:
        """Reads data from a text file and returns a StateNode which is an initial state.
        This should be implemented in subclasses to read problem specific, user-designed file formats. 
        
        This can also set class-level variables.
        """
        raise NotImplementedError


    @staticmethod
    def defaultInitialState() -> StateNode:
        """
        Returns the default initial state (e.g. standard blank board).
        Should be implemented by subclasses.
        
        This can also set class-level variables.
        """
        raise NotImplementedError

    def __init__(self, 
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
                This is more a property of the node than the state, as a tree could 
        current_player_index: the index of the player whose turn it is to take an action. For terminal states, this might be undefined.

        In any subclass of StateNode, the __init__() should take additional parameters that help define its state features.
        Use super.__init__() to call this function and pass appropriate parameters.
        """
        self.parent = parent
        self.last_action = last_action
        self.depth = depth
        self.current_player_index = current_player_index

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
        raise NotImplementedError

    def __str__(self) -> str:
        """Return a string representation of the state."""
        raise NotImplementedError

    def is_endgame_state(self) -> bool:
        """Returns whether or not this state is an endgame state (terminal)"""
        raise NotImplementedError

    def endgame_utility(self, player_index : int) -> Optional[float]:
        """Returns the standard endgame utility of this state from the perspective of the given player.
        If not a terminal (endgame) state, behavior is undefined (but returning None is a good idea)
        
        In many games, this is simply whether the player has won (+1), lost (-1), or tied (0).
        Note that for two-player zero-sum games in general, the utility for the other player is the opposite.

        Instead of using this directly, you should incorporate it into an evaluation function.
        The interpretation of this standard utility can altered by the evaluation function.
        """
        raise NotImplementedError

    def is_legal_action(self, action : Action) -> bool:
        """Returns whether an action is legal from the current state"""
        raise NotImplementedError

    def get_all_actions(self) -> List[Action]:
        """
        Return all legal actions from this state. Actions may be whatever type you wish.
        Note that the ordering may matter for the algorithm (e.g. Alpha-Beta pruning).
        """
        raise NotImplementedError

    def get_next_state(self, action : Action) -> StateNode:
        """ Return a new StateNode that represents the state that results from taking the given action from this state.
        The new StateNode object should have this StateNode (self) as its parent, and action as its last_action.

        -- action is assumed legal (is_legal_action called before), but a ValueError may be passed for illegal actions if desired.
        """
        raise NotImplementedError

    def describe_last_action(self) -> str:
        """Returns a string describing the last_action taken (that resulted in transitioning from parent to this state)
        (Can be None or "None" if the initial state)

        Since the action should have a str() method that describes itself, 
        returning that str suffices - but this state (or its parent) may have additional context
        that can help describe the action in more detail.
        """
        return str(self.last_action)

    def get_path(self) -> Sequence[StateNode]:
        """Returns a sequence (list) of StateNodes representing the path from the initial state to this state.

        You do not need to override this method.
        """
        path = [self]
        s = self.parent
        while s is not None :
            path.append(s)
            s = s.parent
        path.reverse()
        return path

    def get_as_root_node(self) -> StateNode:
        """ Return a copy of this state, but as an initial state node.
        That is, the root of its own game (search) tree 
        """
        s = copy(self)
        s.parent = None
        s.depth = 0
        s.last_action = None
        return s

    def __eq__(self, other) -> bool:
        """
        __eq__ is needed to make StateNode comparable and usable in Sets/Dicts
        This implementation simply checks types and then compares get_state_features().

        You probably want to leave this function alone in subclasses, but
        it could theoretically be overridden to be more efficient.
        """
        if isinstance(other, type(self)) :
            return self.get_state_features() == other.get_state_features()
        return False
    
    def __hash__(self) -> int:
        """
        Leave this function alone; it is important to make StateNode hashable and usable in Sets/Dicts.
        """
        return hash(self.get_state_features())



class GameAgent:
    """ An abstract class for Game Playing Agents, both human and AI. 
        Not meant to be instantiated. All game playing agents will be subclasses of this.
    """

    def __init__(self, *args, **kwargs): 
        """ empty , just absorbes any extra parameters given"""
        pass 

    def pick_action(self, state : StateNode) ->Tuple[Action, Optional[float], Optional[StateNode]]:
        """ To be overridden by subclasses.
        
        Return an action for this agent to do at the given state.
        
        Return 2 things (a 2-tuple): (action, value, leaf_node)
        1) An action for the state 
        2) The expected value of taking that action, as computed by the agent (Optional, could be None)
        3) The StateNode that is the source of the computed value. This would be the leaf state at the end of the expected path in the game tree.  (Optional, could be None)

        """
        raise NotImplementedError

class HumanTextInputAgent(GameAgent):
    """ An interface for human players, using text input for actions """

    def pick_action(self, state : StateNode) -> Tuple[Action, Optional[float], Optional[StateNode]] :
        """
        Gets human input from the console. No value or leaf_state returned.
        """
        action = None
        while action is None:
            inp = input("Type your action >>> ")

            if (action := state.action_type.str_to_action(inp)) not in state.get_all_actions():
                print("Invalid action '{}'.\nYour valid actions include: {}".format(action,
                    str([x.action_to_str() for x in state.get_all_actions()])))
                action = None

        return action, None, None

class HumanGuiAgent(GameAgent):
    """ An interface for human players, using gui input for actions """
    pass

class RandomAgent(GameAgent):
    """ A simple agent that selects a random action. """

    def pick_action(self, state : StateNode, **kwargs) -> Tuple[Action, Optional[float],  Optional[StateNode]] :
        """
        Chooses from one of the possible actions available, using a uniformly random distribution. No value or leaf_state returned.
        """
        return random.choice(state.get_all_actions()), None, None
