from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, Iterable, TypeVar, Dict, Tuple, Callable

from game_algorithms import *
from gamesearch_problem import *

import time

INF = float('inf')

QUIT = ['q', 'Q', 'quit', 'Quit', 'QUIT']
YES = ['y', 'yes', 'Y', 'Yes', 'YES']
NO = ['n', 'no', 'N', 'No', 'NO']
NO_LIMIT = ['inf', 'INF', "Inf", 'infinity', 'infinite', "Infinity", "Infinite",
            'INFINITY', 'INFINITE', 'none', "None", "NONE"]

def ask_yes_no(prompt):
    while True:
        inp = input(prompt  + " >>> ")
        if inp in QUIT:
            quit()
        elif inp in YES:
            return True
        elif inp in NO:
            return False
        else :
            print("Oops, not y[es] or n[o]. ", end = "")

def pick_from_dict(prompt, d):
    print("Options:\n" + "\n".join("\t"+ str(k) for k in d.keys()))
    while True:
        inp = input(prompt  + " >>> ")
        if inp in QUIT:
            quit()
        elif inp in d:
            return d[inp]
        print("Oops, not an option. ", end = "")

def get_int_or_inf(prompt):
    while True:
        inp = input(prompt  + " >>> ")
        if inp in QUIT:
            quit()
        elif inp in NO_LIMIT:
            return INF
        try :
            return int(inp)
        except ValueError:
            print("Oops, not an int or INF.", end="")

def get_int(prompt):
    while True:
        inp = input(prompt + " >>> ")
        if inp in QUIT:
            quit()
        try :
            return int(inp)
        except ValueError:
            print("Oops, not an int! ", end="")

def get_float(prompt):
    while True:
        inp = input(prompt + " >>> ")
        if inp in QUIT:
            quit()
        try :
            return float(inp)
        except ValueError:
            print("Oops, not a float! ", end="")

def get_str_or_default(prompt, default):
    return new_name if (new_name := input(f"{prompt} (default {default}) >>> ").strip()) != "" else default

class AgentWrapper():
    def __init__(self, player_index : int, agent_type : Type[GameAgent], *args, **kwargs ):
        self.player_index : int = player_index
        self.agent_type : Type[GameAgent] = agent_type
        self.agent : GameAgent = None
        if 'name' not in kwargs:
            self.name = 'Agent'
        self.__dict__.update(kwargs)

    def setup_agent(self, gui_callback_fn : Callable[[StateNode, float, Optional[str]],bool]):
        self.agent = self.agent_type(gui_callback_fn = gui_callback_fn, **self.__dict__)

    def choose_action(self, state):
        raise NotImplementedError

    def __str__(self):
        return f"{self.name} (P{self.player_index})" 


class HumanGuiAgentWrapper(AgentWrapper) :

    def __init__(self, player_index: int, *args, **kwargs):
        """ Optional kwargs: (terminal prompt if not included)
                - name (str)
                - verbose (bool)
        """
        if 'name' not in kwargs:
            kwargs['name'] = get_str_or_default("Name:", "Human")

        super().__init__(player_index, HumanGuiAgent, *args, **kwargs)



class HumanTextInputAgentWrapper(AgentWrapper) :

    def __init__(self, player_index: int, *args, **kwargs):
        """ Optional kwargs: (terminal prompt if not included)
                - name (str)
                - verbose (bool)
        """

        if 'verbose' not in kwargs:
            kwargs['verbose'] = ask_yes_no("Be verbose? (Print time elapsed)")


        if 'name' not in kwargs:
            kwargs['name'] = get_str_or_default("Name:", "HumanTextInput")

        super().__init__(player_index, HumanTextInputAgent, *args, **kwargs)


    def choose_action(self, state : StateValue) -> Optional[Tuple[Action, float, Optional[StateNode]]]:
        """ Return an action for the state and its expected utility (from the perspective of the current player). """
        search_start_time = time.perf_counter()
        result = self.agent.pick_action(state)
        elapsed_time = time.perf_counter() - search_start_time
        if self.verbose:
            print("Total elapsed time: {:.4f}".format(elapsed_time))
        return result

class RandomAgentWrapper(AgentWrapper) :

    def __init__(self, player_index: int, *args, **kwargs):
        """ Optional kwargs: (terminal prompt if not included)
                - name (str)
        """

        if 'name' not in kwargs:
            kwargs['name'] = get_str_or_default("Name:", "RandomAgent")

        super().__init__(player_index, RandomAgent, *args, **kwargs)
    
    def choose_action(self, state : StateValue) -> Optional[Tuple[Action, float, Optional[StateNode]]]:
        return self.agent.pick_action(state)



class ReflexAgentWrapper(AgentWrapper) :
    def __init__(self,  player_index : int,
                        eval_fn_dict : Dict[str, Callable[[StateNode, int], float]] = {},
                        *args, **kwargs):
        """ Optional kwargs: (terminal prompt if not included)
                - name (str)
                - evaluation_fn (Callable[[StateNode], float])
                - verbose (bool)
        """


        if 'evaluation_fn' not in kwargs:
            kwargs['evaluation_fn'] = pick_from_dict("Pick evaluation func", eval_fn_dict)
        
        if 'verbose' not in kwargs:
            kwargs['verbose'] = ask_yes_no("Be verbose? (print summary data to console)")

        if 'name' not in kwargs:
            kwargs['name'] = get_str_or_default("Name:", "ReflexAgent")

        super().__init__(player_index, ReflexAgent, *args, **kwargs)


    def choose_action(self, state : StateValue) -> Optional[Tuple[Action, float, Optional[StateNode]]]:
        """ Return an action for the state and its expected utility (from the perspective of the current player). """
        search_start_time = time.perf_counter()
        result = self.agent.pick_action(state)
        elapsed_time = time.perf_counter() - search_start_time
        action, value, leaf = result if result != None else (None, None, None)
        if self.verbose:
            print(("{} evaluates this state (and action {}) as " + ("{:.4f}" if value != None else "{}")).format(self.name, action, value))
            print("Expected next state:\n{}".format(leaf))
            print("Total elapsed time: {:.4f}".format(elapsed_time))
        return result


class GameSearchAgentWrapper(AgentWrapper) :
    def __init__(self,  player_index : int,
                        agent_class : Type[GameSearchAgent], 
                        eval_fn_dict : Dict[str, Callable[[StateNode, int], float]] = {},
                        *args, **kwargs):
        """ Optional kwargs: (terminal prompt if not included)
                - name (str)
                - evaluation_fn (Callable[[StateNode], float])
                - depth_limit (int or math.inf)
                - show_thinking (bool)
                - verbose (bool)
        """

        if 'evaluation_fn' not in kwargs:
            kwargs['evaluation_fn'] = pick_from_dict("Pick evaluation func", eval_fn_dict)
        
        if 'depth_limit' not in kwargs:
            kwargs['depth_limit'] = get_int_or_inf("Pick depth limit (int or inf)")

        if 'show_thinking' not in kwargs:
            kwargs['show_thinking'] = ask_yes_no("Show search process? (callbacks; slower))")
        
        if 'verbose' not in kwargs:
            kwargs['verbose'] = ask_yes_no("Be verbose? (print summary data to console)")

        if 'name' not in kwargs:
            kwargs['name'] = get_str_or_default("Name:", agent_class.__name__)


        super().__init__(player_index, agent_class, *args, **kwargs)

    def setup_agent(self, gui_callback_fn : Callable[[StateNode, float, Optional[str]],bool]):
        if not self.show_thinking  :
            gui_callback_fn = lambda state, value, notes : False

        super().setup_agent(gui_callback_fn)
        
        



    def choose_action(self, state : StateValue) -> Optional[Tuple[Action, float, Optional[StateNode]]]:
        """ Return an action for the state and its expected utility (from the perspective of the current player). """
        self.agent.reset_total_counts()
        search_start_time = time.perf_counter()
        result = self.agent.pick_action(state)
        elapsed_time = time.perf_counter() - search_start_time
        action, value, leaf = result if result != None else (None, None, None)
        self.agent.update_lifetime_counts()
        if self.verbose:
            print(("{} evaluates this state (and action {}) as " + ("{:.4f}" if value != None else "{}")).format(self.name, action, value))
            print("Expected leaf state:\n{}".format(leaf))
            print("Total elapsed time: {:.4f}".format(elapsed_time))
            print("During this search:{} nodes visited, {} leaf evaluations".format(self.agent.total_nodes, self.agent.total_evals))
            print("Over whole lifetime: {} nodes visited, {} leaf evaluations".format(self.agent.lifetime_nodes, self.agent.lifetime_evals))
        return result

class MaximizingSearchAgentWrapper(GameSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=MaximizingSearchAgent ,*args, **kwargs)


class MinimaxSearchAgentWrapper(GameSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=MinimaxSearchAgent ,*args, **kwargs)

class ExpectimaxSearchAgentWrapper(GameSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=ExpectimaxSearchAgent ,*args, **kwargs)


class AlphaBetaSearchAgentWrapper(GameSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=AlphaBetaSearchAgent ,*args, **kwargs)


class MoveOrderingAlphaBetaSearchAgentWrapper(GameSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=MoveOrderingAlphaBetaSearchAgent ,*args, **kwargs)


def callback_stopwatch_decorator(func : Callable, agent_wrapper : AgentWrapper):
    """ Allows an agent_wrapper to decorate their gui_callback_func to return True upon 
    end of a time_limit """
    
    def wrapper_stopwatch(*args, **kwargs):
        value = func(*args, **kwargs)
        run_time = time.perf_counter() - agent_wrapper.start_time
        return value if run_time < agent_wrapper.time_limit else True 
    return wrapper_stopwatch


class IterativeDeepeningSearchAgentWrapper(AgentWrapper) :

    def __init__(self,  player_index : int,
                        agent_class : Type[IterativeDeepeningSearchAgent], 
                        eval_fn_dict : Dict[str, Callable[[StateNode, int], float]] = {},
                        *args, **kwargs):
        """ Optional kwargs: (terminal prompt if not included)
                - name (str)
                - evaluation_fn (Callable[[StateNode], float])
                - time_limit (float)
                - plateau_cutoff (int or math.inf)
                - show_thinking (bool)
                - verbose (bool)
                - super_verbose (bool)
                - super_super_verbose (bool)
        """


        if 'evaluation_fn' not in kwargs:
            kwargs['evaluation_fn'] = pick_from_dict("Pick evaluation func", eval_fn_dict)

        if 'time_limit' not in kwargs:
            kwargs['time_limit'] = get_float("Pick move time limit (seconds)")

        if 'plateau_cutoff' not in kwargs:
            kwargs['plateau_cutoff'] = get_int_or_inf("Pick plateau cutoff (int or inf)")

        if 'show_thinking' not in kwargs:
            kwargs['show_thinking'] = ask_yes_no("Show search process? (callbacks; slower))")
        
        if 'verbose' not in kwargs:
            kwargs['verbose'] = ask_yes_no("Be verbose? (print summary data to console)")

        if kwargs['verbose'] and ('super_verbose' not in kwargs):
            kwargs['super_verbose'] = ask_yes_no("Be *super* verbose?? (include best action /exp value for ALL iter)")
            if kwargs['super_verbose']:
                kwargs['super_super_verbose'] = ask_yes_no("Be *super SUPER* verbose??? (include expected leaf for ALL iter)")

        if 'name' not in kwargs:
            kwargs['name'] = get_str_or_default("Name:", agent_class.__name__)

        super().__init__(player_index, agent_class, *args, **kwargs)

    def setup_agent(self, gui_callback_fn : Callable[[StateNode, float, Optional[str]],bool]):
        if not self.show_thinking  :
            gui_callback_fn = lambda state, value, notes : False

        # Wrap the callback fn with a stopwatch decorator.
        gui_callback_fn = callback_stopwatch_decorator(gui_callback_fn, self)

        super().setup_agent(gui_callback_fn)



    def choose_action(self, state : StateValue) -> Optional[Tuple[Action, float, Optional[StateNode]]]:
        """ Return an action for the state and its expected utility (from the perspective of the current player). """
        self.agent.reset_total_counts()

        self.start_time = time.perf_counter()
        result_list = self.agent.iterative_pick_action(state)
        elapsed_time = time.perf_counter() - self.start_time
        
        action, value, leaf = result_list[-1] if (len(result_list) > 0 and result_list[-1] != None) else (None, None, None)

        self.agent.update_lifetime_counts()

        if self.verbose:
            print(("{} searched to depth {} and evaluated this state (and action {}) as " + ("{:.4f}" if value != None else "{}")).format(self.name, len(result_list), str(action), value))
            print("Expected leaf state:\n{}".format(leaf))
            print("Total elapsed time: {:.4f}".format(elapsed_time))
            print("During this search:{} nodes visited, {} leaf evaluations".format(self.agent.total_nodes, self.agent.total_evals))
            print("Over whole lifetime: {} nodes visited, {} leaf evaluations".format(self.agent.lifetime_nodes, self.agent.lifetime_evals))

            if self.super_verbose:
                print("Iterative results:")
                for c, result in enumerate(result_list):
                    a, v, l = result if result != None else (None, None, None)
                    print("Depth {:2d}: Best action is {} at exp value {:.4f}".format(c+1, a, v))
                    if self.super_super_verbose:
                        print("\tExpected leaf state:\n{}".format(l))

        return result_list[-1] if result_list else None



class IDMaximizingSearchAgentWrapper(IterativeDeepeningSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=type("ID " + MaximizingSearchAgent.__name__, (IterativeDeepeningSearchAgent, MaximizingSearchAgent), {}) ,*args, **kwargs)


class IDMinimaxSearchAgentWrapper(IterativeDeepeningSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=type("ID " + MinimaxSearchAgent.__name__, (IterativeDeepeningSearchAgent, MinimaxSearchAgent), {}) ,*args, **kwargs)

class IDExpectimaxSearchAgentWrapper(IterativeDeepeningSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=type("ID " + ExpectimaxSearchAgent.__name__, (IterativeDeepeningSearchAgent, ExpectimaxSearchAgent), {}) ,*args, **kwargs)


class IDAlphaBetaSearchAgentWrapper(IterativeDeepeningSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=type("ID " + AlphaBetaSearchAgent.__name__, (IterativeDeepeningSearchAgent, AlphaBetaSearchAgent), {}) ,*args, **kwargs)


class IDMoveOrderingAlphaBetaSearchAgentWrapper(IterativeDeepeningSearchAgentWrapper) :

    def __init__(self, *args, **kwargs):
        super().__init__(agent_class=type("ID " + MoveOrderingAlphaBetaSearchAgent.__name__, (IterativeDeepeningSearchAgent, MoveOrderingAlphaBetaSearchAgent), {}) ,*args, **kwargs)




class MonteCarloTreeSearchAgentWrapper(AgentWrapper) :

    def __init__(self,  player_index : int,
                        *args, **kwargs):
        """ Optional kwargs: (terminal prompt if not included)
                - name (str)
                - exploration_bias (float)
                - time_limit (float)
                - show_thinking (bool)
                - verbose (bool)
        """

        if 'exploration_bias' not in kwargs:
            kwargs['exploration_bias'] = get_float("Exploration Bias (float):")

        if 'time_limit' not in kwargs:
            kwargs['time_limit'] = get_float("Pick move time limit (seconds)")

        if 'show_thinking' not in kwargs:
            kwargs['show_thinking'] = ask_yes_no("Show search process? (callbacks; slower))")
        
        if 'verbose' not in kwargs:
            kwargs['verbose'] = ask_yes_no("Be verbose? (print summary data to console)")

        if 'name' not in kwargs:
            kwargs['name'] = get_str_or_default("Name:", "MCTS")

        super().__init__(player_index, MonteCarloTreeSearchAgent, *args, **kwargs)



    def setup_agent(self, gui_callback_fn : Callable[[StateNode, float, Optional[str]],bool]):
        if not self.show_thinking :
            gui_callback_fn = lambda state, value, notes : False

        # Wrap the callback fn with a stopwatch decorator.
        gui_callback_fn = callback_stopwatch_decorator(gui_callback_fn, self)

        super().setup_agent(gui_callback_fn)
        

    def choose_action(self, state : StateValue) -> Optional[Tuple[Action, float, Optional[StateNode]]]:
        """ Return an action for the state and its expected utility (from the perspective of the current player). """
        self.agent.reset_total_counts()

        self.start_time = time.perf_counter()
        result = self.agent.iterative_pick_action(state)
        elapsed_time = time.perf_counter() - self.start_time
        
        action, value, leaf = result if result != None else (None, None, None)

        self.agent.update_lifetime_counts()

        if self.verbose:
            print(("{} performed {} rollouts and evaluated this state (and action {}) as " + ("{:.4f}" if value != None else "{}")).format(self.name, self.total_rollouts, str(action), value))
            print("Expected leaf state:\n{}".format(leaf))
            print("Total elapsed time: {:.4f}".format(elapsed_time))
            print("Rollouts over whole lifetime: {} ".format(self.agent.lifetime_rollouts))

        return result


