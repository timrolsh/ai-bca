# Lab 2: Games
# Name(s): Krish Arora, Timothy Rolshud
# Email(s): kriaro24@bergen.org, timrol24@bergen.org

from connectfour_game import *
from tictactoe_game import *
from nim_game import *
from roomba_game import *

"""
Some useful built-in python methods:
    any(list-like) - returns if at least one True
    all(list-like) - returns if all are True
    sum(list-like) - returns sum of all (??)
    list.count(item) - returns count of items in a list/tuple


Check out the game-specific methods at the BOTTOM of each game definition file.
"""

## General purpose evaluation functions: ###########

def endgame_score_heur_zero_eval_fn(state : StateNode, player_index : int):
    """ Given a state and the player_index of the "maximizer",
    returns the standard endgame utility for that player_index. 
    Usually, winning is +1, losing is -1, and tieing is 0.

    Given a non-endgame NimGameState, gives a constant (and useless) heuristic 
    evaluation of 0.
    """
    if state.is_endgame_state():
        return state.endgame_utility(player_index)
    
    return 0

def faster_endgame_score_heur_zero_eval_fn(state : StateNode, player_index : int):
    """ Given a state and the player_index of the "maximizer",
    returns an AUGMENTED standard endgame utility for that player_index that rewards winning faster and losing slower.

    Winning is >= +1, losing is <= -1, and tieing is 0. 
    An endgame node with the same result but a lower depth will have a score with greater magnitude.

    This does produce inconsistent values for states depending on their position in their search tree; 
    searching from different roots will yield different results. 

    Given a non-endgame NimGameState, gives a constant (and useless) heuristic 
    evaluation of 0.
    """
    if state.is_endgame_state():
        return state.endgame_utility(player_index) * (1 + 1 / (state.depth + 1))
    
    return 0

        

## TicTacToe specific evaluation functions: ###########

## Edges are valued least, center valued highest.
space_weights = {   (0,0): .2, (0,1): .1, (0,2): .2,
                    (1,0): .1, (1,1): .3, (1,2): .1,
                    (2,0): .2, (2,1): .1, (2,2): .2 }

def space_weights_eval_tictactoe(state : TicTacToeGameState, player_index : int):
    """
    Given a NimGameState and the player_index of the "maximizer",
    returns the standard endgame utility for that player_index. (+1 for win, -1 for loss)

    Given a non-endgame TicTacToeGameState, estimate the value
    (expected utility) of the state from player_index's view.

    Return a linearly weighted sum of the "value" of each piece's position.
    Maximizer's pieces are + value, Minimizer's pieces are - value.
    Try tweaking the weights in space_weights!

    This evaluation function is zero-sum, and only returns values in the range of (-1,+1).

    """
    if state.is_endgame_state():
        return state.endgame_utility(player_index)
    eval_score = 0
    for r in range(TicTacToeGameState.num_rows):
        for c in range(TicTacToeGameState.num_cols):
            piece = state.get_piece_at(r,c)
            if piece == TicTacToeGameState.EMPTY:
                continue
            elif piece == player_index:
                eval_score += space_weights[(r,c)]
            else:
                eval_score -= space_weights[(r,c)]
    return eval_score

def custom_eval_tictactoe(state : TicTacToeGameState, player_index : int):
    """ 
    Given a TicTacToeGameState and the player_index of the "maximizer",
    return an endgame utility for endgame states (should be derived from state.endgame_utility, >= +1 for win, >= -1 for loss), 
    or for non-endgame state estimate the value in a different and better way than empty rows. 
    
    This evaluation function ideally should be zero-sum, and only return estimated values in the range of (-1,+1) 

    Although "perfect" tictactoe heuristics do exist, it would make more sporting AIs to have a "pretty good" heuristic.
    You can take inspiration from our problem sets! 
    """
    # TODO
    raise NotImplementedError


# Add new evaluation functions to this dictionary.
tictactoe_functions = {
    "endgame score": endgame_score_heur_zero_eval_fn,
    "faster endgame score": faster_endgame_score_heur_zero_eval_fn,
    "spaces weighted": space_weights_eval_tictactoe,
    "custom eval": custom_eval_tictactoe
}



## Nim specific evaluation functions: ###########

def empty_rows_eval_nim(state : NimGameState, player_index : int):
    """ 
    Given a NimGameState and the player_index of the "maximizer",
    returns the standard endgame utility for that player_index. (+1 for win, -1 for loss)

    Given a non-endgame NimGameState, estimate the value as
    the fraction of rows that are empty - The more empty rows, the better!
    
    This is NOT a zero-sum evaluation - all players get the same heuristic evaluation.
    This models all players as wanting to empty rows faster - quite possibly erroneously!
    """
    if state.is_endgame_state():
        return state.endgame_utility(player_index)

    return [state.get_stones_in_pile(p) for p in range(state.get_num_piles())].count(0) / state.get_num_piles()


def custom_eval_nim(state : NimGameState, player_index : int):
    """ 
    Given a NimGameState and the player_index of the "maximizer",
    return an endgame utility for endgame states (should be derived from state.endgame_utility, >= +1 for win, >= -1 for loss), 
    or for non-endgame state estimate the value in a different and better way than empty rows. 
    
    This evaluation function ideally should be zero-sum, and only return estimated values in the range of (-1,+1) 

    There DOES exist a perfect, mathematical way to evaluate a NimGameState as a winning or losing position.
    Such a perfect evaluation would allow a Reflex agent to play just as well as a full Minimax player.
    But, you don't HAVE to do that - you may come up with something that would be more *sporting* for a human to play against.
    """
    # TODO 
    raise NotImplementedError


# Add new evaluation functions to this dictionary.
nim_functions = {
    "endgame score": endgame_score_heur_zero_eval_fn,
    "faster endgame score": faster_endgame_score_heur_zero_eval_fn,
    "empty rows": empty_rows_eval_nim,
    "custom eval": custom_eval_nim
}


## Connect-four specific evaluation functions: ###########

chain_length_weights = {1: .01, 2: .03, 3: .10}
def chains_weights_connectfour(state : ConnectFourGameState, player_index : int):
    """
    Given a state and the player_index of the "maximizer",
    returns an AUGMENTED standard endgame utility for that player_index that rewards winning faster and losing slower.
    
    Given a non-endgame ConnectFourGameState, estimate the value
    (expected utility) of the state from player_index's view.

    
    Return a linearly weighted sum of the "value" of each piece's chains.
    Maximizer's chains are + value, Minimizer's chains are - value.
    Try tweaking the weights in chain_length_weights!

    This evaluation function is zero-sum, and only returns values in the range of (-1,+1) 
    """
    if state.is_endgame_state():
        return state.endgame_utility(player_index) * (1 + 1 / (state.depth + 1))


    score = 0
    for chain_len in chain_length_weights:
        score += state.get_num_chains(chain_len, player_index) * chain_length_weights[chain_len]
        score -= state.get_num_chains(chain_len, player_index %2 + 1) * chain_length_weights[chain_len]
    return max(min(.99,score), -.99)

def custom_eval_connectfour(state : ConnectFourGameState, player_index : int):
    """ 
    Given a ConnectFourGameState and the player_index of the "maximizer",
    return an endgame utility for endgame states (should be derived from state.endgame_utility, >= +1 for win, >= -1 for loss), 
    or for non-endgame state estimate the value in a different and better way than empty rows. 
    
    This evaluation function ideally should be zero-sum, and only return estimated values in the range of (-1,+1) 

    Although "perfect" connectfour heuristics do exist, they are... overly complex for the scope of this lab.
    Plus, it would make more sporting AIs to have a "pretty good" heuristic, but flawed.
    """

    raise NotImplementedError

# Add new evaluation functions to this dictionary.
connectfour_functions =  {
        "endgame score": endgame_score_heur_zero_eval_fn,
        "faster endgame score": faster_endgame_score_heur_zero_eval_fn,
        "chains weighted": chains_weights_connectfour,
        "custom eval": custom_eval_tictactoe,

}


## Roomba Race specific evaluation functions: ###########

def defensive_eval_roomba(state : RoombaRaceGameState, player_index : int):
    """ 
    Given a RoombaRaceGameState and the player_index of the "maximizer",
    return an endgame utility for endgame states (should be derived from state.endgame_utility, >= +1 for win, >= -1 for loss), 
    or for non-endgame state estimate the value in a different and better way than empty rows. 
    
    This evaluation function ideally should be zero-sum, and only return estimated values in the range of (-1,+1) 

    The goal here is not necessarily an ideal heuristic, but one that produces human-like emergent behavior when searching to non-terminal states.
    This evaluation function should produce an agent who general plays "defensively".
    """
    # TODO
    raise NotImplementedError


def aggressive_eval_roomba(state : RoombaRaceGameState, player_index : int):
    """ 
    Given a RoombaRaceGameState and the player_index of the "maximizer",
    return an endgame utility for endgame states (should be derived from state.endgame_utility, >= +1 for win, >= -1 for loss), 
    or for non-endgame state estimate the value in a different and better way than empty rows. 
    
    This evaluation function ideally should be zero-sum, and only return estimated values in the range of (-1,+1) 

    The goal here is not necessarily an ideal heuristic, but one that produces human-like emergent behavior when searching to non-terminal states.
    This evaluation function should produce an agent who general plays "aggressively".
    """
    # TODO
    raise NotImplementedError


# Add new evaluation functions to this dictionary.
roomba_functions = {
    "endgame score": endgame_score_heur_zero_eval_fn,
    "faster endgame score": faster_endgame_score_heur_zero_eval_fn,
    "custom aggressive": aggressive_eval_roomba,
    "custom defensive": defensive_eval_roomba
}






