# Lab 1, Part 2a: Heuristics.
# Name(s): Timothy Rolshud, Krish Arora

from math import sqrt
from search_heuristics import *
from slidepuzzle_problem import *

INF = float('inf')

#### Lab 1, Part 2a: Heuristics #################################################

# Implement these two heuristic functions for SlidePuzzleState.

""" Return the Hamming distance (number of tiles out of place) of the SlidePuzzleState """


def slidepuzzle_hamming(state: SlidePuzzleState) -> float:
    hamming_distance = 0
    for i in range(0, len(state.tiles)):
        for j in range(0, len(state.tiles[i])):
            if state.tiles[i][j] != 0:
                if state.tiles[i][j] != i * len(state.tiles[i]) + j:
                    hamming_distance += 1
    return hamming_distance


""" Return the sum of Manhattan distances between tiles and goal of the SlidePuzzleState """


def slidepuzzle_manhattan(state: SlidePuzzleState) -> float:
    """ The Manhattan heuristic function returns the sum of the Manhattan distances (“city block
distance”, or sum of the vertical and horizontal distances) of each block to their goal positions
(again, not including the empty space). The intuition is similar to the Hamming heuristic; the
closer each block is to where it should finish, the closer to the goal."""
    manhattan_distance = 0
    n = len(state.tiles)

    for i in range(n):
        for j in range(n):
            tile = state.tiles[i][j]
            if tile != 0:
                for k in range(n):
                    for l in range(n):
                        if tile == k * n + l:
                            manhattan_distance += abs(i - k) + abs(j - l)
    return manhattan_distance


SLIDEPUZZLE_HEURISTICS = {
    "Zero": zero_heuristic,
    "Arbitrary": arbitrary_heuristic,
    "Hamming": slidepuzzle_hamming,
    "Manhattan": slidepuzzle_manhattan
}
