from search_heuristics import *
from roomba_problem import *
INF = float('inf')

#### Lab 1, Part 2a: Heuristics #################################################


def roomba_manhattan_onegoal(state: RoombaState) -> float:
    """A heuristic for RoombaState assuming there is only one goal tile.
    Return the manhattan distance to that dirty tile.
    """
    for r in range(state.get_height()):
        for c in range(state.get_width()):
            if state.get_terrain(Coordinate(r, c)) in (DIRTY_CARPET, DIRTY_FLOOR):
                # Return manhattan distance between roomba and goal positions

                return abs(r - state.position.row) + abs(c - state.position.col)

    return 0  # in the case of no goal, we will return a meaningless value


def roomba_manhattan_multigoal(state: RoombaState) -> float:
    """ A heuristic for RoombaState if there is more than one goal tile. 
    Return the manhattan distance to the closest goal.
    """
    min_dist = INF

    for r in range(state.get_height()):
        for c in range(state.get_width()):
            if state.get_terrain(Coordinate(r, c)) in (DIRTY_CARPET, DIRTY_FLOOR):
                # look for smallest manhattan distance between roomba and goal positions
                dist = abs(r - state.position.row) + \
                    abs(c - state.position.col)
                min_dist = min(min_dist, dist)
    return min_dist


# This is a named list of heuristics for the Roomba problem.
# Add any more that you wish to use in the GUI
ROOMBA_HEURISTICS = {
    "Zero": zero_heuristic,
    "Arbitrary": arbitrary_heuristic,
    "Manhattan Dist. (one goal)": roomba_manhattan_onegoal,
    "Manhattan Dist. (closest)": roomba_manhattan_multigoal
}
