from typing import *
from search_problem import StateNode
INF = float('inf')

#### Lab 1, Part 2a: Heuristics #################################################


def zero_heuristic(state: StateNode):
    """ A very unhelpful heuristic. Returns 0"""
    return 0


def arbitrary_heuristic(state: StateNode):
    """ A arbitrary but deterministic heuristic . """
    return hash(state) % 100
