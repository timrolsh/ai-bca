"""
Play games between 2 agents on the console with text

Usage:
    python lab2_play_text.py [GAME] [INITIAL_STATE_FILE] ")
    GAME can be tictactoe, nim, connectfour, or roomba
    INITIAL_STATE_FILE is a path to a text file or 'default'
"""
from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, List, Tuple, Callable

from traceback import format_exc
from sys import argv
from game_algorithms import *
from agent_wrappers import *
from gamesearch_problem import StateNode, Action
from eval_functions import roomba_functions, connectfour_functions, tictactoe_functions, nim_functions

from connectfour_game import ConnectFourGameState
from tictactoe_game import TicTacToeGameState
from nim_game import NimGameState
from roomba_game import RoombaRaceGameState
import time

all_fn_dicts = { RoombaRaceGameState: roomba_functions,
    ConnectFourGameState: connectfour_functions,
    TicTacToeGameState: tictactoe_functions,
    NimGameState: nim_functions}

GAME_CLASSES : Dict[str, Type[StateNode]] = {"connectfour":ConnectFourGameState, "tictactoe": TicTacToeGameState, "nim": NimGameState, "roomba": RoombaRaceGameState}

AGENT_NAMES =  ["Human", "Random" , "Reflex", "MaxDFS", "Minimax", "Expectimax", "AlphaBeta", "MoveOrderingAlphaBeta", "MCTS"]

BASIC_AGENTS = {"Human": HumanTextInputAgentWrapper, "Random": RandomAgentWrapper , "Reflex" : ReflexAgentWrapper}
SEARCH_AGENTS = {"MaxDFS" : MaximizingSearchAgentWrapper, "Minimax": MinimaxSearchAgentWrapper, "Expectimax": ExpectimaxSearchAgentWrapper, 
                    "AlphaBeta" : AlphaBetaSearchAgentWrapper, "MoveOrderingAlphaBeta" : MoveOrderingAlphaBetaSearchAgentWrapper}

ITERATIVE_SEARCH_AGENTS = {"MaxDFS" : IDMaximizingSearchAgentWrapper, "Minimax": IDMinimaxSearchAgentWrapper, "Expectimax": IDExpectimaxSearchAgentWrapper, 
                    "AlphaBeta" : IDAlphaBetaSearchAgentWrapper, "MoveOrderingAlphaBeta" : IDMoveOrderingAlphaBetaSearchAgentWrapper}

ASSYMETRIC_AGENTS = {"MCTS": MonteCarloTreeSearchAgentWrapper}

if len(argv) < 3 :
    print("Usage:    python lab2_play_text.py [GAME] [INITIAL_STATE_FILE] [AGENT_1] [AGENT_2] ...")
    print("          GAME can be " + " or ".join("'{}'".format(game) for game in GAME_CLASSES))
    print("          INITIAL_STATE_FILE is a path to a text file, OR \"default\"")
    quit()

if (argv[1] not in GAME_CLASSES):
    print("1st argument should be one of the following: {}".format(str(list(GAME_CLASSES.keys()))))
    quit()

game_class = GAME_CLASSES[argv[1]]

eval_fn_dict = all_fn_dicts[game_class]


initial_state = game_class.defaultInitialState() if argv[2] == 'default' else game_class.readFromFile(argv[2])

# Set up agents

playing_agents = {}

for p, name in enumerate(game_class.player_names):
    print("Agent Options:\n" + "\n".join("{}: {}".format(n,s) for n,s in enumerate(AGENT_NAMES)))

    k = input("Please pick an agent for P{} [{}]: >>> ".format(p,name))
    while k not in AGENT_NAMES:
        if k in (str(i) for i in range(len(AGENT_NAMES))):
            k = AGENT_NAMES[int(k)]
            break
        k = input("Please pick an agent's name or number from the list: >>> ")
    
    agenttype = type(None)
    if k in ITERATIVE_SEARCH_AGENTS:
        if ask_yes_no("Iterative Deepening? (y/n)"):
            agenttype = ITERATIVE_SEARCH_AGENTS[k]
        else:
            agenttype = SEARCH_AGENTS[k]
    elif k in ASSYMETRIC_AGENTS:
        agenttype = ASSYMETRIC_AGENTS[k]
    elif k in BASIC_AGENTS:
        agenttype = BASIC_AGENTS[k]
    else:
        print("Uh oh something went wrong")
        quit()
    
    playing_agents[p] = agenttype(player_index = p, eval_fn_dict = eval_fn_dict, show_thinking = False)
    playing_agents[p].setup_agent(lambda s, f, m : False)



# Run the game
game_state :StateNode = initial_state
print(game_state)
while not game_state.is_endgame_state():

    current_player = game_state.current_player_index
    current_agent = playing_agents[current_player]
    print("P{} [{}] {}'s turn:".format(current_player, game_class.player_names[current_player], current_agent.name))

    start_time = time.perf_counter()
    result = current_agent.choose_action(game_state)

    time_elapsed = time.perf_counter() - start_time
    if time_elapsed < 1:
        time.sleep(1 - time_elapsed)

    if result == None:
        print("P{} [{}] {} forfeits!".format(current_player, game_class.player_names[current_player], current_agent.name))
        quit()
    action, _, _ = result
    print("P{} [{}] {} chooses {}".format(current_player, game_class.player_names[current_player], current_agent.name, action))

    game_state = game_state.get_next_state(action)
    print(game_state)


utils = [game_state.endgame_utility(p) for p in range(len(game_state.player_names))]

if len( winners := [i for i,u in enumerate(utils) if u > 0]) == 1:
    winner = winners[0]
    print("P{} [{}] {} wins!".format(winner, game_class.player_names[winner], playing_agents[winner].name))
else :
    if utils.count(utils[0]) == len(utils) :
        print("Tie!")
    else :
        print("It's... complicated.")
        for i, u in enumerate(utils):
            print("P{} [{}] {} scored {:.4f}!".format(i, game_class.player_names[i],playing_agents[i].name, u))

