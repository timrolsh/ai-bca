# Timothy Rolshud and Krish Arora

from search_heuristics import *
from spotlessroomba_problem import *

# TODO If applicable, argue for why this is admissible / consistent!
def spotlessroomba_first_heuristic(state : SpotlessRoombaState)  -> float:
    # TODO implement a custom, nontrivial heuristic. Rename appropriately
    raise NotImplementedError

# TODO If applicable, argue for why this is admissible / consistent!
def spotlessroomba_second_heuristic(state : SpotlessRoombaState)  -> float:
    # TODO implement a custom, nontrivial heuristic. Rename appropriately
    raise NotImplementedError

# TODO if you wish, implement more heuristics!

# TODO Update heuristic names and functions below. If you make more than two, add them here.
SPOTLESSROOMBA_HEURISTICS = {"Zero" : zero_heuristic,
                        "Arbitrary": arbitrary_heuristic, 
                        "Custom Heur. 1": spotlessroomba_first_heuristic,
                        "Custom Heur. 2" : spotlessroomba_second_heuristic
                        }
