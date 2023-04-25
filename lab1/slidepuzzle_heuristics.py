# Lab 1, Part 2a: Heuristics.
# Name(s):
from search_heuristics import *
from slidepuzzle_problem import *

INF = float('inf')

#### Lab 1, Part 2a: Heuristics #################################################

# Implement these two heuristic functions for SlidePuzzleState.

""" Return the Hamming distance (number of tiles out of place) of the SlidePuzzleState """


def slidepuzzle_hamming(state: SlidePuzzleState) -> float:
    raise NotImplementedError


""" Return the sum of Manhattan distances between tiles and goal of the SlidePuzzleState """


def slidepuzzle_manhattan(state: SlidePuzzleState) -> float:
    raise NotImplementedError


SLIDEPUZZLE_HEURISTICS = {
    "Zero": zero_heuristic,
    "Arbitrary": arbitrary_heuristic,
    "Hamming": slidepuzzle_hamming,
    "Manhattan": slidepuzzle_manhattan
}
