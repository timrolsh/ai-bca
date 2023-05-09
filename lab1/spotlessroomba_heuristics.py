# Timothy Rolshud and Krish Arora

from search_heuristics import *
from spotlessroomba_problem import *

"""
return the index of the closest distance coordinate to given coordinate in the list
"""


def closest_index(coord: Coordinate, coordinates: list[Coordinate], distance_function: Callable[[Coordinate, Coordinate], float]) -> int:
    lowest_distance: float = 0
    lowest_index: int = 0
    for a, other_coord in enumerate(coordinates):
        current_distance: float = distance_function(coord, other_coord)
        if current_distance < lowest_distance:
            lowest_distance = current_distance
            lowest_index = a
    return lowest_index


"""
given two coordinates, get the euclidian distance (distance formula) between them
"""


def euclidian_distance(coord1: Coordinate, coord2: Coordinate) -> float:
    return ((coord1.row - coord2.row) ** 2 + (coord1.col - coord2.col) ** 2) ** (1/2)


"""
given two coordinates, get the manhatten distance 
(cannot go diagonally, and have to go by side lengths of trinangle)
"""


def manhatten_distance(coord1: Coordinate, coord2: Coordinate) -> float:
    return abs(coord1.row - coord2.row) + (coord1.col - coord2.col)


"""
helper for both heuristics as the code for them will be mostly the
same except for the method which they use to calculate distance
"""


def heuristic_helper(state, distance_function: Callable[[Coordinate, Coordinate], float]):
    sum: float = 0
    dirty_tiles: list[Coordinate] = list(state.dirty_locations)
    current_location: Coordinate = state.position
    while len(dirty_tiles) > 0:
        closest: int = closest_index(
            current_location, dirty_tiles, distance_function)
        sum += distance_function(current_location, dirty_tiles[closest])
        current_location = dirty_tiles[closest]
        del dirty_tiles[closest]
    return sum


"""
Calculate the estimated euclidian path that the roomba has to go through to clean all of the remaining tiles from this state.
The path length is calculated in the following way:
- at the current state, calculate the Euclidian distance to the next dirty tile. 
- go to the next dirty tile, and calculate the Euclidian distance to the cloest dirty tile to that one.
- repeat until all of the tiles have been cleaned up. the sum of all the Euclidian distances is the heuristic value

This heuristic must be admissable because the roomba cannot physically do Euclidian distance travel to every single
location and it will always have to go a little bit more. Also, the algorithm to clean all the tiles from the current
state seems like the best case scenario, keep going to the tiles cloesst to you until you clean all of tiles. 
Ultimately, because this algorithm accounts for a shorter distance than the Roomba can actually travel and takes into 
account the best case scenario, it will be over-optimistic and will be admissable. 

This heuristic is consistent because the fewer remaining dirty tiles there are to clean, the lower the sum of the
distances will be, representing you being closer to completion. As you extend further out in the wrong direction, the number will increase as the best case scenario distance is now increasing.
"""


def euclidian_heuristic(state: SpotlessRoombaState) -> float:
    # TODO implement a custom, nontrivial heuristic. Rename appropriately

    return heuristic_helper(state, euclidian_distance)


"""
Same algorithm as the other heuristic function, calculate the sum of distances from closest dirty tiles. However,
distance is calculated with Manhatten distance as opposed to Euclidian distance. 

This heuristic is consistent for the same reason that the other heuristic is consistent.

This heuristis is still admissable because although the Manhatten distance is a realistic distance for the Roomba to
travel and not an underestimate in terms of difference, the heuristic still considers the best case scenario for the
Roomba's path, still making the heurstic admissable. 
"""


def manhatten_heuristic(state: SpotlessRoombaState) -> float:
    # TODO implement a custom, nontrivial heuristic. Rename appropriately
    return heuristic_helper(state, manhatten_distance)


SPOTLESSROOMBA_HEURISTICS = {
    "Zero": zero_heuristic,
    "Arbitrary": arbitrary_heuristic,
    "Euclidian Path Estimate": euclidian_heuristic,
    "Manhatten Path Estimate": manhatten_heuristic
}
