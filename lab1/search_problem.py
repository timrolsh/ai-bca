from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, Iterable, TypeVar, List
from abc import ABC, abstractmethod
from copy import copy
"""
An abstract framework for a goal-search problem.

The Action and StateNode classes are not meant to be instantiated or used directly.
Rather, they serve as an abstract superclasses for different environment/problem representations.

Your search algorithms will work with StateNode objects, making them generalizable
for all kinds of problems.
"""


class Action(ABC):
    """ An abstract object that represents an action in an environment """

    def __str__(self) -> str:
        """ Returns a string that describes this action """
        raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        """ Returns whether other is equivalent in value """
        if not isinstance(other, type(self)):
            return False
        raise NotImplementedError

    def __hash__(self) -> int:
        """ Returns a hash for this action, making it usable in Sets/Dicts."""
        raise NotImplementedError


SN = TypeVar("SN", bound="StateNode")


class StateNode(ABC):
    """ An abstract object that represents a a state in an environment. 
    It also serves as a search tree "node" which includes information about the state's
    parent, last action taken (that leads to this state), and the length/cost of the path
    that led to this state.
    """

    # Type Hints allow for the optional type declaration of instance variables, like Java
    parent: Optional[StateNode]  # type:ignore
    last_action: Optional[Action]
    depth: int
    path_cost: float

    @staticmethod
    @abstractmethod
    def readFromFile(filename: str) -> StateNode:
        """Reads data from a text file and returns a StateNode which is an initial state.
        This should be implemented in subclasses to read problem specific, user-designed file formats. 
        """
        raise NotImplementedError

    def __init__(self,
                 parent: Optional[StateNode],
                 last_action: Optional[Action],
                 depth: int,
                 path_cost: float):
        """Creates a StateNode that represents a state of the environment and context for how the agent gets 
        to this state (the path, aka a series of state-action transitions).

        Keyword Arguments:
        parent -- the preceding StateNode along the path to reach this state. None, for an initial state.
        last_action -- the preceding action taken along the path to reach this state. None, for an initial state. 
        depth -- the number of state-action transitions taken in the path to reach this state.
        path_cost -- the accumulated cost of the entire path to reach this state

        In any subclass of StateNode, the __init__() should take additional parameters that help define its state features.
        Use super.__init__() to call this function and pass appropriate parameters.
        """
        self.parent = parent
        self.last_action = last_action
        self.depth = depth
        self.path_cost = path_cost

    @abstractmethod
    def get_state_features(self: SN) -> Hashable:
        """Returns a fully featured representation of the state.

        This should return something consistent, immutable, and hashable - 
        generally, tuples of primitives, strings, or other tuples (generally no lists or objects).

        If two StateNode objects represent the same state, get_state_features() should return the same for both objects.
        However, two StateNodes with identical state features may not represent the same node of the search tree -
        that is, they may have different parents, last actions, path lengths/costs etc...
        """
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        """Return a string representation of the state."""
        raise NotImplementedError

    @abstractmethod
    def is_goal_state(self) -> bool:
        """Returns if a goal (terminal) state."""
        raise NotImplementedError

    @abstractmethod
    def is_legal_action(self, action: Action) -> bool:
        """Returns whether an action is legal from the current state"""
        raise NotImplementedError

    @abstractmethod
    def get_all_actions(self) -> Iterable[Action]:
        """Return all legal actions from this state. Actions may be whatever type you wish."""
        raise NotImplementedError

    def describe_last_action(self) -> str:
        """Returns a string describing the last_action taken (that resulted in transitioning from parent to this state)
        (Can be None or "None" if the initial state)

        Since the action should have a str() method that describes itself, 
        returning that str suffices - but this state (or its parent) may have additional context
        that can help describe the action in more detail.
        """
        return str(self.last_action)

    @abstractmethod
    def get_next_state(self: SN, action: Action) -> SN:
        """ Return a new StateNode that represents the state that results from taking the given action from this state.
        The new StateNode object should have this StateNode (self) as its parent, and action as its last_action.

        -- action is assumed legal (is_legal_action called before), but a ValueError may be passed for illegal actions if desired.
        """
        raise NotImplementedError

    def get_path(self: SN) -> Sequence[SN]:
        """Returns a sequence (list) of StateNodes representing the path from the initial state to this state.

        You do not need to override this method.
        """
        path: List[SN] = [self]
        s = self.parent
        while s is not None:
            # type checkers break down here
            path.append(s)  # type: ignore
            s = s.parent
        path.reverse()
        return path

    def get_as_root_node(self: SN) -> SN:
        """ Return a copy of this state, but as an initial state node.
        That is, the root of its own search tree 
        """
        s = copy(self)
        s.parent = None
        s.last_action = None
        s.path_cost = 0.0
        s.depth = 0
        return s

    def __lt__(self, other) -> bool:
        """
        Leave this function alone; it is needed to make tuple comparison work with heapq (PriorityQueue). 
        It doesn't actually describe any ordering.
        """
        return True

    def __eq__(self, other) -> bool:
        """
        __eq__ is needed to make StateNode comparable and usable in Sets/Dicts
        This implementation simply checks types and then compares get_state_features().

        You probably want to leave this function alone in subclasses, but
        it could theoretically be overridden to be more efficient.
        """
        if isinstance(other, type(self)):
            return self.get_state_features() == other.get_state_features()
        return False

    def __hash__(self) -> int:
        """
        Leave this function alone; it is important to make StateNode hashable and usable in Sets/Dicts.
        """
        return hash(self.get_state_features())
