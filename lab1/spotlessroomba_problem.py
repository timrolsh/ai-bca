# Timothy Rolshud and Krish Arora

from __future__ import annotations
from typing import *

from roomba_problem import *

# Translations between dirty and clean versions of the terrain.
DIRTY_TERRAIN = {FLOOR : DIRTY_FLOOR, CARPET : DIRTY_CARPET}
CLEAN_TERRAIN = {DIRTY_FLOOR : FLOOR, DIRTY_CARPET : CARPET}

class SpotlessRoombaState(RoombaState):
    """
    A subclass of RoombaState. The main difference is that the roomba agent's goal is to 
    reach (and clean) ALL the dirty spots, not just one of them.
    """

    dirty_locations : Tuple[Coordinate,...]
    # These are already mentioned in the superclasses, but more specifically typed here
    parent : Optional[SpotlessRoombaState]
     
    #Overridden
    @staticmethod
    def readFromFile(filename : str) -> SpotlessRoombaState:
        """Reads data from a text file and returns a SpotlessRoombaState which is an initial state.
        """
        with open(filename, 'r') as file:
            # This first part is the same as the RoombaState...

            # First line has the number of rows and columns
            max_r, max_c = (int(x) for x in file.readline().split())
            # Second line has the initial row/column of the roomba agent
            init_r, init_c = (int(x) for x in file.readline().split())
            # Remaining lines are the layout grid of 
            grid = tuple( tuple(file.readline().strip()) for r in range(max_r))
            # Sanity check - is the grid really the right size?
            assert (len(grid) == max_r and all( len(row) == max_c for row in grid))

            # Once again, the grid itself is effectively the same for each state, 
            # except now we must keep track of which dirty spots have been cleaned or not yet.
            # Instead of updating the grid from state to state, 
            # we will instead keep a list (tuple) of which of the locations are still dirty. 
            # This makes tracking the differences between states easier, faster, 
            # and more memory efficient, among other advantages.
            dirty : List[Coordinate] = []
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    if grid[i][j] in (DIRTY_CARPET, DIRTY_FLOOR):
                        dirty.append(Coordinate(i,j))

            # Now re-do the grid with the dirty spots changed to their clean counterparts
            grid = tuple( tuple(CLEAN_TERRAIN.get(Terrain(x), Terrain(x)) for x in row) for row in grid)

            return SpotlessRoombaState(dirty_locations = tuple(dirty),
                                position = Coordinate(init_r, init_c),
                                grid = grid,
                                parent = None,
                                last_action = None,
                                depth = 0,
                                path_cost = 0)


    def __init__(self, 
                dirty_locations : Tuple[Coordinate,...],
                position: Coordinate, 
                grid: Tuple[Tuple[Terrain,...],...], 
                parent : Optional[SpotlessRoombaState], 
                last_action: Optional[RoombaAction],  #Note that actions are (relative) Coordinates!
                depth : int, 
                path_cost : float = 0.0) :
        """
        Creates a SpotlessRoombaState, which represents a state of the roomba's environment .

        Keyword Arguments (in addition to RoombaState arguments):
        dirty_locations -- A tuple of all the not-yet cleaned (visited) locations that are (still) dirty in the grid. 
        """
        super().__init__(position = position, grid = grid, parent = parent, last_action = last_action, depth = depth, path_cost = path_cost)
        self.dirty_locations = dirty_locations
        


    """ Overridden methods from RoombaState and StateNode """
    
    # Override   
    def get_terrain(self, coord : Coordinate) -> Terrain:
        terrain = self.grid[coord.row][coord.col]
        return DIRTY_TERRAIN[terrain] if coord in self.dirty_locations else terrain 


    # Override
    def get_state_features(self) :
        """Returns a full feature representation of the state.

        Once again, the grid  is essentially the same for each state, except we must 
        keep track of which dirty spots have been cleaned or not yet.

        Therefore, we'll use dirty_locations as a feature (plus roomba agent position), since it captures the 
        difference between two states sufficiently. Note that this is far more time and memory efficient 
        than using the whole grid as a feature, which must be updated for each state.

        If two SpotlessRoombaStateNode objects represent the same state, get_features() should return the same for both objects.
        Note, however, that two states with identical features may have been arrived at from different paths.
        """
        return (self.position, self.dirty_locations) 

    # Override
    def __str__(self) -> str:
        """Return a string representation of the state."""
        s = list(super().__str__()) 
        # Draw all dirty spots 
        for coord in self.dirty_locations:
            pos = coord.row * (self.get_width()+1) + coord.col
            s[pos] = DIRTY_TERRAIN.get(Terrain(s[pos]),Terrain(s[pos]))
        return "".join(s)

    # Override
    
    def is_goal_state(self) -> bool:
        """Returns if a goal (terminal) state.
        If there are no more dirty locations, the roomba has finished cleaning!
        """
        return len(self.dirty_locations) == 0

    # Override
    def get_next_state(self, action : RoombaAction) -> SpotlessRoombaState:
        """ Return a new SpotlessRoombaState that represents the state that results from taking the given action from this state.
        The new SpotlessRoombaState object should have this (self) as its parent, and action as its last_action.

        -- action is assumed legal (is_legal_action called before)
        """
        new_pos = action.applyTo(self.position)
        step_cost = TRANSITION_COSTS[self.get_terrain(new_pos)]
        # If moving onto a dirty spot, it gets cleaned!
        return SpotlessRoombaState( 
            dirty_locations = tuple(x for x in self.dirty_locations if x != new_pos) 
                                if new_pos in self.dirty_locations 
                                else self.dirty_locations,
            position = new_pos,
            grid = self.grid, 
            last_action = action,
            parent = self,
            depth = self.depth + 1,
            path_cost = self.path_cost + step_cost)

