"""
Visualizing GUI for your solutions to Lab 2.
Use it to test your algorithms and evaluation functions.

Usage:
    python lab2_test_gui.py [GAME] [INITIAL_STATE_FILE]
    GAME can be tictactoe, nim, connectfour, or roomba
    INITIAL_STATE_FILE is a path to a text file or 'default'
"""
from __future__ import annotations
from typing import Optional, Any, Hashable, Sequence, List, Tuple, Callable


from traceback import format_exc
from sys import argv
import time

from math import sqrt
from tkinter import * # Tk, Canvas, Frame, Listbox, Button, Checkbutton, IntVar, StringVar, Spinbox, Label
from game_algorithms import *
from agent_wrappers import *
from gamesearch_problem import StateNode, Action
from eval_functions import roomba_functions, connectfour_functions, tictactoe_functions, nim_functions

from connectfour_game import ConnectFourGameState, ConnectFourAction
from tictactoe_game import TicTacToeGameState, TicTacToeAction
from nim_game import NimGameState, NimAction
from roomba_game import RoombaRaceGameState, RoombaRaceAction, Coordinate, Terrain, FLOOR, WALL, CLEANED

all_fn_dicts = { RoombaRaceGameState: roomba_functions,
    ConnectFourGameState: connectfour_functions,
    TicTacToeGameState: tictactoe_functions,
    NimGameState: nim_functions}
### GUI too big? Change this number
MAX_HEIGHT = 350


INF = float('inf')
# For tic-tac-toe, connectfour, and nim
PIECE, FRAME , EMPTY, TEXT = ('piece_1', 'piece_2'),'frame', 'empty', 'text'
# For nim
STONE = 'stone'
# For roomba race
AGENT, PATH = ('agent_1', 'agent_2'), ('path_1', 'path_2')

COLORS = {FLOOR : 'green', WALL : 'gray25', CLEANED : 'white',
          AGENT[0]:"orange red", AGENT[1]:"blue", PATH[0]:"orange red", PATH[1]:"blue",
          PIECE[0]: 'red', PIECE[1]: 'yellow', FRAME: 'blue',EMPTY: 'white' , TEXT: 'black',
          STONE : 'grey'}


AGENT_NAMES =  ["Random" , "Reflex", "MaxDFS", "Minimax", "Expectimax", "AlphaBeta", "MoveOrderingAlphaBeta", "MCTS"]

BASIC_AGENTS = {"Human": HumanGuiAgentWrapper, "Random": RandomAgentWrapper , "Reflex" : ReflexAgentWrapper}
SEARCH_AGENTS = {"MaxDFS" : MaximizingSearchAgentWrapper, "Minimax": MinimaxSearchAgentWrapper, "Expectimax": ExpectimaxSearchAgentWrapper, 
                    "AlphaBeta" : AlphaBetaSearchAgentWrapper, "MoveOrderingAlphaBeta" : MoveOrderingAlphaBetaSearchAgentWrapper}

ITERATIVE_SEARCH_AGENTS = {"MaxDFS" : IDMaximizingSearchAgentWrapper, "Minimax": IDMinimaxSearchAgentWrapper, "Expectimax": IDExpectimaxSearchAgentWrapper, 
                    "AlphaBeta" : IDAlphaBetaSearchAgentWrapper, "MoveOrderingAlphaBeta" : IDMoveOrderingAlphaBetaSearchAgentWrapper}

ASSYMETRIC_AGENTS = {"MCTS": MonteCarloTreeSearchAgentWrapper}


STEP_TIME_OPTIONS = (0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09,
                    0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 5.0)

CUTOFF_OPTIONS = tuple( ['INF'] + list(range(1,100)))

INITIAL_WAITING = 0
SEARCHING_RUNNING = 1
SEARCHING_PAUSED = 2
SEARCHING_STEP = 3
TERMINATING_EARLY = 4
FINISHED_COMPLETE = 5
FINISHED_INCOMPLETE = 6
FINISHED_COMPLETE_DISP_LEAF = 9
FINISHED_INCOMPLETE_DISP_LEAF = 10
FINISHED_NO_RESULT = 11
SEARCH_ERROR = -1


VALID_STATUS_TRANSITIONS = {
    None: (INITIAL_WAITING,),
    INITIAL_WAITING : (SEARCHING_RUNNING, SEARCHING_PAUSED, SEARCHING_STEP),
    SEARCHING_RUNNING : (SEARCHING_PAUSED, SEARCHING_STEP, TERMINATING_EARLY, FINISHED_COMPLETE, FINISHED_NO_RESULT, SEARCH_ERROR, INITIAL_WAITING),
    SEARCHING_PAUSED : (SEARCHING_RUNNING, SEARCHING_STEP, TERMINATING_EARLY, FINISHED_COMPLETE, FINISHED_NO_RESULT, SEARCH_ERROR, INITIAL_WAITING),
    SEARCHING_STEP : (SEARCHING_RUNNING, SEARCHING_PAUSED, TERMINATING_EARLY, FINISHED_COMPLETE, FINISHED_NO_RESULT, SEARCH_ERROR, INITIAL_WAITING),
    TERMINATING_EARLY : (FINISHED_COMPLETE, FINISHED_NO_RESULT, SEARCH_ERROR),
    FINISHED_COMPLETE : (FINISHED_COMPLETE_DISP_LEAF,INITIAL_WAITING),
    FINISHED_COMPLETE_DISP_LEAF : (FINISHED_COMPLETE,INITIAL_WAITING),
    FINISHED_NO_RESULT : (INITIAL_WAITING,),
    SEARCH_ERROR : tuple()
}

STATUS_TEXT = { INITIAL_WAITING: "P{} [{}]'s turn: Pick an agent or click to input a move.",
                SEARCHING_RUNNING:"P{} [{}] {} is searching...",
                SEARCHING_PAUSED: "P{} [{}] {} is paused.",
                SEARCHING_STEP:   "P{} [{}] {} is paused.",
                TERMINATING_EARLY: "P{} [{}] {} is terminating early...",
                FINISHED_COMPLETE: "P{} [{}] {} completed successfully. Displaying best move found.",
                FINISHED_COMPLETE_DISP_LEAF: "P{} [{}] {} completed successfully. Displaying expected leaf node.",
                FINISHED_NO_RESULT: "P{} [{}] {} terminated with no result.",
                SEARCH_ERROR: "Something went wrong during search. Check the console for the exception stack trace."
                }

class TestGameGui:
    def __init__(self, master, initial_state:StateNode, canvas_height, canvas_width, eval_fn_dict : Dict[str, Callable[[StateNode, int], float]]):
        self.master = master

        self.initial_state = initial_state
        self.current_state = initial_state

        self.search_root_state = initial_state
        self.display_state = initial_state

        self.search_result_best_leaf_state = None
        self.search_result_best_action = None

        self.eval_fn_dict = eval_fn_dict

        self.search_start_time = None

        self.current_agent : AgentWrapper = None


        #########################################################################################

        self.canvas = Canvas(master, height=canvas_height, width=canvas_width, bg='white')

        self.canvas.grid(row = 0, columnspan = 5) #pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', lambda *args : self.draw_background() or self.draw_path_to_state() )
        self.canvas.bind('<Button-1>', self.click_canvas_attempt_action)

        ################################################

        gameplay_button_frame = Frame(master)
        gameplay_button_frame.grid(row = 1, columnspan = 5, sticky = N, padx = 3)

        self.restart_button = Button(gameplay_button_frame, text="Restart Game",
                    command= self.restart_game, width = 15, pady = 3)
        self.restart_button.grid(row = 0, column = 0, sticky = NE)

        self.undo_move_button = Button(gameplay_button_frame, text="Undo Last Move",
                    command= self.undo_last_move, width = 15, pady = 3)
        self.undo_move_button.grid(row = 0, column = 1, sticky = NW)

        self.history_button = Button(gameplay_button_frame, text="Toggle History",
                    command= self.toggle_display_history, width = 15, pady = 3)
        self.history_button.grid(row = 0, column = 2, sticky = NW)

        ###################################################

        status_output_frame = Frame(master, padx = 3)
        status_output_frame.grid(row = 2, columnspan = 5,sticky = N)

        self.status = None

        self.status_text = StringVar()
        self.status_label = Label(status_output_frame, textvariable = self.status_text, anchor = CENTER, bg = "lightblue", pady = 3, justify = CENTER, relief = GROOVE)
        self.status_label.grid(row= 0,sticky = N)


        self.counter_dict = {}

        self.eval_fn_result_text = StringVar()
        self.eval_fn_result_text.set('Expected utility of state: {:7s}'.format("TBD"))

        self.eval_fn_result_label = Label(status_output_frame, textvariable = self.eval_fn_result_text, bg = "lightgreen", justify = CENTER, anchor = CENTER, relief = GROOVE)
        self.eval_fn_result_label.config(font=("Courier", 12))
        self.eval_fn_result_label.grid(row= 1,sticky = N)

        self.callback_msg_text = StringVar()
        self.callback_msg_text.set('Callback messages go here')

        self.callback_msg_label = Label(status_output_frame, textvariable = self.callback_msg_text, bg = "lightblue", justify = CENTER, anchor = CENTER, relief = GROOVE)
        self.callback_msg_label.config(font=("Courier", 12))
        self.callback_msg_label.grid(row=2 ,sticky = N)

        self.counter_text_1 = StringVar()
        self.counter_label_1 = Label(status_output_frame, textvariable = self.counter_text_1, fg = "blue", anchor = CENTER)
        self.counter_label_1.grid(row= 3,sticky = N)




        #########################################################################################


        algorithm_frame = Frame(master)
        algorithm_frame.grid(row = 3, column = 0, rowspan = 2, sticky = NW, padx = 3)

        algorithm_label = Label(algorithm_frame, text="Game Search Algorithm:")
        algorithm_label.grid(row = 0, sticky = NW)

        self.agent_listbox = Listbox(algorithm_frame, selectmode = BROWSE, height = len(AGENT_NAMES), exportselection = 0)
        self.agent_listbox.grid(row= 1, sticky = NW)
        for item in AGENT_NAMES:
            self.agent_listbox.insert(END, item)
        self.agent_listbox.select_set(0) # This only sets focus on the first item.
        self.agent_listbox.bind('<<ListboxSelect>>', self.on_agent_changed)
        self.agent_listbox.event_generate("<<ListboxSelect>>")

        self.current_agent_name = self.get_agent_selection()


        self.iterative_deepening_state = IntVar()
        self.iterative_deepening_state.set(0)
        self.iterative_deepening_checkbox = Checkbutton(algorithm_frame, text='Iterative Deepening', variable=self.iterative_deepening_state, command=self.on_agent_changed)
        self.iterative_deepening_checkbox.grid(row= 2, column = 0, sticky = NW)


        #########################################################################################


        eval_fn_frame = Frame(master)
        eval_fn_frame.grid(row = 3, column = 1, sticky = NW, padx = 3)


        eval_label = Label(eval_fn_frame, text="Evaluation Functions")
        eval_label.grid(row = 0, sticky = NW)
        # set self.eval_fn_dict in init of subclass
        #TODO
        self.eval_fn_listbox = Listbox(eval_fn_frame, selectmode = BROWSE, height = len(self.eval_fn_dict), exportselection = 0)
        self.eval_fn_listbox.grid(row= 1, sticky = NW)
        for item in self.eval_fn_dict.keys():
            self.eval_fn_listbox.insert(END, item)
        self.eval_fn_listbox.select_set(0) # This only sets focus on the first item.
        self.eval_fn_listbox.event_generate("<<ListboxSelect>>")

        self.current_eval_fn_name = self.get_eval_fn_selection()

        self.print_state_eval_button = Button(eval_fn_frame, text="Print State Eval", #Print Expected Path
                            command=self.print_eval_display_state,width = 15, pady = 3)
        self.print_state_eval_button.grid(row= 2, column = 0, sticky = NW)

        #########################################################################################
        search_options_frame = Frame(master)
        search_options_frame.grid(row = 4, column = 1, sticky = NW, padx = 3)

        cutoff_frame = Frame(search_options_frame)
        cutoff_frame.grid(row = 0, sticky = NW, pady = 3)

        self.depth_limit_plateau_cutoff_label = Label(cutoff_frame, text="Depth Limit:")
        self.depth_limit_plateau_cutoff_label.grid(row = 0, column = 0, sticky = NW)

        self.depth_limit_plateau_cutoff_spinbox = Spinbox(cutoff_frame,
            values=CUTOFF_OPTIONS, width = 5, wrap = True)
        self.depth_limit_plateau_cutoff_spinbox.grid(row= 0, column = 1, sticky = NW, padx = 5)
        while(self.depth_limit_plateau_cutoff_spinbox.get() != "INF") :
            self.depth_limit_plateau_cutoff_spinbox.invoke('buttonup')

        self.recent_plateau = "INF"
        self.recent_depth_limit = "INF"


        self.time_limit_label = Label(cutoff_frame, text="Time Limit (s):")
        self.time_limit_label.grid(row = 1, column = 0, sticky = NW)

        self.time_limit_spinbox = Spinbox(cutoff_frame,
            values=CUTOFF_OPTIONS, width = 5, wrap = True)
        self.time_limit_spinbox.grid(row= 1, column = 1, sticky = NW, padx = 5)
        while(self.time_limit_spinbox.get() != "INF") :
            self.time_limit_spinbox.invoke('buttonup')


        exploration_bias_frame = Frame(search_options_frame)
        exploration_bias_frame.grid(row = 3, sticky = NW, pady = 3)

        self.exploration_bias_label = Label(exploration_bias_frame, text="Expl. Bias:" )
        self.exploration_bias_label.grid(row = 0, column = 0, sticky = NW)
        self.exploration_bias_state = DoubleVar()
        self.exploration_bias_state.set(1000)
        self.exploration_bias_entry = Entry(exploration_bias_frame, textvariable = self.exploration_bias_state, width = 6)
        self.exploration_bias_entry.grid(row = 0, column = 1, sticky = NW)
        self.exploration_bias_label_2 = Label(exploration_bias_frame, text="* sqrt(2)")
        self.exploration_bias_label_2.grid(row = 0, column = 2, sticky = NW)

        #########################################################################################

        run_options_frame = Frame(master)
        run_options_frame.grid(row = 3, column = 2, rowspan = 2, sticky = NW, padx = 3)

        self.reset_button = Button(run_options_frame, text="Terminate Search", # Discard Search Results
                            command= self.terminate_search_or_discard_results, width = 15, pady = 3)
        self.reset_button.grid(row = 1, column = 0, sticky = NW)


        self.run_pause_button = Button(run_options_frame, text="Start Search", # Pause Search, Play Move
                            command= self.toggle_run_pause_or_play_move, width = 15, pady = 3)
        self.run_pause_button.grid(row= 2, column = 0, sticky = NW)

        self.step_button = Button(run_options_frame, text="Step Search", # Display Search [Move/Exp Leaf Node]
                            command=self.step_or_toggle_display_action_leaf, width = 15, pady = 3)
        self.step_button.grid(row= 3, column = 0, sticky = NW)


        self.fly_blind_search_button = Button(run_options_frame, text="FLY BLIND SEARCH", # Pause Search, Play Move
                            command= self.fly_blind_search, width = 15, pady = 3, fg = 'blue')
        self.fly_blind_search_button.grid(row = 4, column = 0, sticky = NW)

        #########################################################################################

        status_output_settings_frame = Frame(master, padx = 3,width = 30)
        status_output_settings_frame.grid(row = 3, rowspan = 2, column = 3,sticky = NW)


        Label(status_output_settings_frame, text = "Mid-Search Visualization: ").grid(row= 0, column = 0, sticky = NW)

        self.visualize_callbacks_state = IntVar()
        self.visualize_callbacks_state.set(1)
        self.visualize_callbacks_checkbox = Checkbutton(status_output_settings_frame, text='Draw state on callbacks?', variable=self.visualize_callbacks_state)
        self.visualize_callbacks_checkbox.grid(row= 1, column = 0, sticky = NW)

        self.print_status_state = IntVar()
        self.print_status_state.set(1)
        self.print_status_checkbox = Checkbutton(status_output_settings_frame, text='Display search progress text?', variable=self.print_status_state)
        self.print_status_checkbox.grid(row= 2, column = 0, sticky = NW)

        step_time_spinbox_frame = Frame(status_output_settings_frame)
        step_time_spinbox_frame.grid(row = 3, column = 0,sticky = NW)

        self.step_time_label = Label(step_time_spinbox_frame, text = "Step time: ")
        self.step_time_label.grid(row= 0, column = 0, sticky = NW)

        self.step_time_spinbox = Spinbox(step_time_spinbox_frame,
        values=STEP_TIME_OPTIONS, format="%3.2f", width = 4)
        self.step_time_spinbox.grid(row= 0, column = 1, sticky = NW)
        while self.step_time_spinbox.get() != "0.1" :
            self.step_time_spinbox.invoke('buttonup')

        Label(status_output_settings_frame, text = "Post-Search Console Print: ").grid(row= 4, column = 0, sticky = NW)

        self.verbose_print_state = IntVar()
        self.verbose_print_state.set(1)
        self.verbose_print_checkbox = Checkbutton(status_output_settings_frame, text='Verbose details?', variable=self.verbose_print_state)
        self.verbose_print_checkbox.grid(row= 5, column = 0, sticky = NW)

        self.id_verbose_print_state = IntVar()
        self.id_verbose_print_state.set(1)
        self.id_verbose_print_checkbox = Checkbutton(status_output_settings_frame, text='Verbose iterative details?', variable=self.id_verbose_print_state)
        self.id_verbose_print_checkbox.grid(row= 6, column = 0, sticky = NW)

        self.print_path_states_button = Button(status_output_settings_frame, text="Print Current Search Path.", #Print Expected Path
                            command=self.print_path_states,width = 20, pady = 3)
        self.print_path_states_button.grid(row= 7, column = 0, sticky = NW)


        ###############################################################

        self.update_status_and_ui(INITIAL_WAITING)


    def update_status_and_ui(self, newstatus = INITIAL_WAITING):
        if newstatus == self.status: # No change?
            return

        assert newstatus in VALID_STATUS_TRANSITIONS[self.status]

        self.status = newstatus
        
        self.status_text.set(STATUS_TEXT[self.status].format(self.current_state.current_player_index, 
                                                        self.current_state.player_names[self.current_state.current_player_index],
                                                        self.current_agent_name))
        if newstatus == INITIAL_WAITING :
            self.restart_button['state'] = NORMAL
            self.restart_button['bg'] = 'orange red'
            self.undo_move_button['state'] = NORMAL
            self.undo_move_button['bg'] = 'DodgerBlue2'
            self.history_button['state'] = NORMAL
            self.history_button['bg'] = 'orchid1'

            self.reset_button['state'] = DISABLED
            self.reset_button['text'] = 'Terminate Search'
            self.reset_button['bg'] = 'grey'

            # Can choose new algorithm settings
            self.depth_limit_plateau_cutoff_spinbox['state'] = NORMAL
            self.time_limit_spinbox['state'] = NORMAL

            self.agent_listbox['state'] = NORMAL
            self.eval_fn_listbox['state'] = NORMAL
            self.iterative_deepening_checkbox['state'] = NORMAL
            self.exploration_bias_label['state'] = NORMAL
            self.exploration_bias_label_2['state'] = NORMAL
            self.exploration_bias_entry['state'] = NORMAL
            self.on_agent_changed() # set certain UI features based on alg

            self.run_pause_button['state'] = NORMAL
            self.run_pause_button['text'] = 'Start Search'
            self.run_pause_button['bg'] = 'green'

            self.step_button['state'] = NORMAL
            self.step_button['text'] = 'Step Search'
            self.step_button['bg'] = 'yellow'

            self.print_path_states_button['state'] = DISABLED
            self.print_path_states_button['text'] = "Print Current Search Path"

            self.fly_blind_search_button['state'] = NORMAL
            self.fly_blind_search_button['bg'] = 'VioletRed1'


        elif newstatus in (SEARCHING_RUNNING,
                            SEARCHING_PAUSED, SEARCHING_STEP):
            self.restart_button['state'] = DISABLED
            self.restart_button['bg'] = 'grey'
            self.undo_move_button['state'] = DISABLED
            self.undo_move_button['bg'] = 'grey'
            self.history_button['state'] = DISABLED
            self.history_button['bg'] = 'grey'

            self.reset_button['state'] = NORMAL
            self.reset_button['text'] = 'Terminate Search'
            self.reset_button['bg'] = 'red'

            # Cannot choose new algorithm settings
            self.depth_limit_plateau_cutoff_spinbox['state'] = DISABLED
            self.time_limit_spinbox['state'] = DISABLED

            self.agent_listbox['state'] = DISABLED
            self.eval_fn_listbox['state'] = DISABLED
            self.iterative_deepening_checkbox['state'] = DISABLED
            self.exploration_bias_label['state'] = DISABLED
            self.exploration_bias_label_2['state'] = DISABLED
            self.exploration_bias_entry['state'] = DISABLED

            self.step_button['state'] = NORMAL
            self.run_pause_button['state'] = NORMAL

            self.print_path_states_button['state'] = NORMAL
            self.print_path_states_button['text'] = "Print Current Search Path"

            if newstatus == SEARCHING_RUNNING:
                self.run_pause_button['text'] = 'Pause Search'
                self.run_pause_button['bg'] = 'orange'
            elif newstatus == SEARCHING_PAUSED: # moving away == starting searching
                self.run_pause_button['text'] = 'Continue Search'
                self.run_pause_button['bg'] = 'green'
            elif newstatus == SEARCHING_STEP: # moving away == starting searching
                self.run_pause_button['text'] = 'Continue Search'
                self.run_pause_button['bg'] = 'green'
                # If we're stepping, obviously user means to see things
                self.visualize_callbacks_state.set(1)
                self.print_status_state.set(1)

            self.fly_blind_search_button['state'] = DISABLED
            self.fly_blind_search_button['bg'] = 'grey'

        elif newstatus in (TERMINATING_EARLY,):
            self.reset_button['state'] = DISABLED
            self.run_pause_button['state'] = DISABLED
            self.step_button['state'] = DISABLED
            self.print_path_states_button['state'] = DISABLED

        elif newstatus in (FINISHED_COMPLETE,):
            self.reset_button['state'] = NORMAL
            self.reset_button['text'] = 'Discard Search'
            self.reset_button['bg'] = 'red'

            self.run_pause_button['state'] = NORMAL
            self.run_pause_button['text'] = 'Play Best Move'
            self.run_pause_button['bg'] = 'green'

            if self.search_result_best_leaf_state != None:
                self.step_button['state'] = NORMAL
                self.step_button['text'] = 'Show Expected Path'
                self.step_button['bg'] = 'violet'
            else:
                self.step_button['state'] = DISABLED
                self.step_button['text'] = 'Show Expected Path'
                self.step_button['bg'] = 'grey'

            self.print_path_states_button['state'] = NORMAL
            self.print_path_states_button['text'] = "Print Expected Path"

        elif newstatus in (FINISHED_COMPLETE_DISP_LEAF,):
            self.step_button['state'] = NORMAL
            self.step_button['text'] = 'Show Best Move'

        elif newstatus in (FINISHED_NO_RESULT,) :
            self.reset_button['state'] = NORMAL
            self.reset_button['text'] = 'Discard Search'

            self.run_pause_button['state'] = DISABLED
            self.run_pause_button['text'] = 'Play Best Move'
            self.run_pause_button['bg'] = 'grey'

            self.step_button['state'] = DISABLED
            self.step_button['text'] = 'Show Expected Path'
            self.run_pause_button['bg'] = 'grey'

            self.print_path_states_button['state'] = DISABLED
            self.print_path_states_button['text'] = "Print Expected Path"
        elif newstatus in (SEARCH_ERROR,):
            self.restart_button['state'] = DISABLED
            self.undo_move_button['state'] = DISABLED
            self.history_button['state'] = DISABLED
            self.reset_button['state'] = DISABLED
            # Cannot choose new algorithm settings
            self.depth_limit_plateau_cutoff_spinbox['state'] = DISABLED
            self.time_limit_spinbox['state'] = DISABLED
            self.agent_listbox['state'] = DISABLED
            self.eval_fn_listbox['state'] = DISABLED
            self.iterative_deepening_checkbox['state'] = DISABLED

            self.run_pause_button['state'] = DISABLED
            self.step_button['state'] = DISABLED
            self.print_path_states_button['state'] = DISABLED
            self.fly_blind_search_button['state'] = DISABLED

        return newstatus

    def print_path_states(self) :

        if self.status in (FINISHED_COMPLETE,  FINISHED_COMPLETE_DISP_LEAF):
            print_state = self.search_result_best_leaf_state
            print_str = "Expected Path states: (length {})"
        else:
            print_state = self.display_state
            print_str = "Current Search Path states: (length {})"

        if print_state == None:
            print("No path to print.")
            return

        print(print_str.format(print_state.depth))
        for n, state in enumerate(print_state.get_path()):
            if n > 0:
                print('P{} [{}] chooses {}'.format(str(n), state.parent.current_player_index,
                        state.player_names[state.parent.current_player_index],
                         state.describe_last_action()))
            print(str(state))


    # def print_path_actions(self) :
    #     print_state = self.display_state if self.status not in (FINISHED_COMPLETE, FINISHED_INCOMPLETE) else self.best_leaf_state
    #     print("Expected Path actions: (length {})".format(print_state.get_path_length()))
    #     for n, state in enumerate(print_state.get_path()):
    #         if n > 0:
    #             print('{}: {}'.format(str(n), state.describe_previous_action()))

    def on_agent_changed(self, event = None):
        agent = self.get_agent_selection()
        id = self.iterative_deepening_state.get()

        if agent in ITERATIVE_SEARCH_AGENTS :
            self.iterative_deepening_checkbox['state'] = NORMAL
        else :
            self.iterative_deepening_checkbox['state'] = DISABLED

        if agent in ITERATIVE_SEARCH_AGENTS and id:
            self.time_limit_label['state'] = NORMAL
            self.time_limit_spinbox['state'] = NORMAL

            if self.depth_limit_plateau_cutoff_label['text'] != "Plateau Cutoff:":
                self.recent_depth_limit = self.depth_limit_plateau_cutoff_spinbox.get()
                self.depth_limit_plateau_cutoff_label['text'] = "Plateau Cutoff:"

                while(self.depth_limit_plateau_cutoff_spinbox.get() != self.recent_plateau) :
                    self.depth_limit_plateau_cutoff_spinbox.invoke('buttonup')
        else:
            self.time_limit_label['state'] = DISABLED
            self.time_limit_spinbox['state'] = DISABLED
            if self.depth_limit_plateau_cutoff_label['text'] != "Depth Limit:":
                self.recent_plateau = self.depth_limit_plateau_cutoff_spinbox.get()
                self.depth_limit_plateau_cutoff_label['text'] = "Depth Limit:"

                while(self.depth_limit_plateau_cutoff_spinbox.get() != self.recent_depth_limit) :
                    self.depth_limit_plateau_cutoff_spinbox.invoke('buttonup')

        if agent in ASSYMETRIC_AGENTS:
            self.time_limit_label['state'] = NORMAL
            self.time_limit_spinbox['state'] = NORMAL
            self.depth_limit_plateau_cutoff_label['state'] = DISABLED
            self.depth_limit_plateau_cutoff_spinbox['state'] = DISABLED
            
            self.exploration_bias_label['state'] = NORMAL
            self.exploration_bias_label_2['state'] = NORMAL
            self.exploration_bias_entry['state'] = NORMAL

            self.eval_fn_listbox['state'] = DISABLED
        else:
            self.depth_limit_plateau_cutoff_label['state'] = NORMAL
            self.depth_limit_plateau_cutoff_spinbox['state'] = NORMAL

            self.exploration_bias_label['state'] = DISABLED
            self.exploration_bias_label_2['state'] = DISABLED
            self.exploration_bias_entry['state'] = DISABLED

            self.eval_fn_listbox['state'] = NORMAL

    def get_agent_selection(self) :
        return self.agent_listbox.get(self.agent_listbox.curselection()[0])
         

    def get_eval_fn_selection(self) :
        return self.eval_fn_listbox.get(self.eval_fn_listbox.curselection()[0])

    def print_eval_display_state(self):
        fn_name = self.get_eval_fn_selection()
        eval_fn = self.eval_fn_dict[self.get_eval_fn_selection()]
        print("Evaluation function {} on this state: \n{}\n".format(fn_name, self.display_state))
        cpi = self.display_state.current_player_index
        for i, p in enumerate(self.display_state.player_names):
            print("P{} [{}] values it at: {}".format(i,p, eval_fn(self.display_state,i)), end="")
            print(" (Current Player) " if i == cpi else "")
        if self.display_state.is_endgame_state():
            print("Is endgame state!")


    def verify_parameters(self, fly_blind):
        if self.current_agent_name  in SEARCH_AGENTS:
            try:
                if (cutoff := self.depth_limit_plateau_cutoff_spinbox.get()) != 'INF':
                    cutoff = int(cutoff)
            except Exception:
                self.update_status_and_ui(INITIAL_WAITING)
                self.status_text.set("Cutoff not a valid int or INF. ('INF' for no limit)")
                return False
        if (self.iterative_deepening_state.get() and self.current_agent_name in ITERATIVE_SEARCH_AGENTS) or self.current_agent_name in ASSYMETRIC_AGENTS:
            try:
                time_limit = float(self.time_limit_spinbox.get())
                if fly_blind and (time_limit == INF) :
                    self.update_status_and_ui(INITIAL_WAITING)
                    self.status_text.set("Woah there - don't \"fly blind\" with no time limit!")
                    return False
            except Exception:
                self.update_status_and_ui(INITIAL_WAITING)
                self.status_text.set("Time Limit not a valid number. ('INF' for no limit)")
                return False

        if self.current_agent_name in ASSYMETRIC_AGENTS:
            try:
                exploration_bias = self.exploration_bias_state.get()
            except Exception:
                self.update_status_and_ui(INITIAL_WAITING)
                self.status_text.set("Exploration Bias is not a valid number. (Default 1000)")
                return False

        return True


    def run_search(self, fly_blind):
        #run?

        id = self.iterative_deepening_state.get()
        eval_fn = self.eval_fn_dict[self.current_eval_fn_name]

        player_index = self.search_root_state.current_player_index

        depth_limit_plateau_cutoff = int(dlpc) if (dlpc := self.depth_limit_plateau_cutoff_spinbox.get()) != 'INF' else float(dlpc)

        time_limit = float(self.time_limit_spinbox.get())
        exploration_bias = float(self.exploration_bias_state.get())

        verbose = self.verbose_print_state.get()
        id_verbose = self.id_verbose_print_state.get()

        show_thinking = True


        if self.current_agent_name in ASSYMETRIC_AGENTS:
            self.current_agent = ASSYMMETRIC_AGENTS[self.current_agent_name](
                                    player_index = player_index,
                                    exploration_bias = exploration_bias,
                                    time_limit = time_limit,
                                    show_thinking = show_thinking,
                                    plateau_cutoff = depth_limit_plateau_cutoff,
                                    verbose = verbose,
                                    name = self.current_agent_name,
                                    )

        elif (id and self.current_agent_name in ITERATIVE_SEARCH_AGENTS):
            self.current_agent = ITERATIVE_SEARCH_AGENTS[self.current_agent_name](
                                    player_index = player_index,
                                    evaluation_fn = eval_fn,
                                    time_limit = time_limit,
                                    show_thinking = show_thinking,
                                    plateau_cutoff = depth_limit_plateau_cutoff,
                                    verbose = verbose,
                                    super_verbose = id_verbose,
                                    super_super_verbose = id_verbose,
                                    name = "ID " + self.current_agent_name,
                                    )
        elif self.current_agent_name in SEARCH_AGENTS:
            self.current_agent = SEARCH_AGENTS[self.current_agent_name](
                                    player_index = player_index,
                                    evaluation_fn = eval_fn,
                                    depth_limit = depth_limit_plateau_cutoff,
                                    verbose = verbose,
                                    show_thinking = show_thinking,
                                    name = self.current_agent_name
                                    )
        elif self.current_agent_name in BASIC_AGENTS:
            self.current_agent = BASIC_AGENTS[self.current_agent_name](
                                    player_index = player_index,
                                    evaluation_fn = eval_fn,
                                    verbose = verbose,
                                    name = self.current_agent_name
                                    )

        else: 
            print("Something went wrong... Yell at Mr. Wang")

        self.current_agent.setup_agent(self.alg_callback_blind if fly_blind  else self.alg_callback )
        result = self.current_agent.choose_action(self.search_root_state)

        if result == None:
            self.search_result_best_action , self.search_result_best_exp_util, self.search_result_best_leaf_state  = None, None, None
            self.update_status_and_ui(FINISHED_NO_RESULT)
        else:
            self.search_result_best_action ,  self.search_result_best_exp_util, self.search_result_best_leaf_state = result
            self.update_status_and_ui(FINISHED_COMPLETE)


    def start_search(self, event = None, initial_status = SEARCHING_RUNNING, fly_blind = False):
        self.current_agent_name = self.get_agent_selection()
        self.current_eval_fn_name = self.get_eval_fn_selection()

        self.update_status_and_ui(initial_status)
        if not self.verify_parameters(fly_blind):
            return
        try:
            self.search_root_state = self.current_state.get_as_root_node()
            self.run_search(fly_blind)
            if self.search_result_best_action != None :
                self.visualize_state(self.search_root_state.get_next_state(self.search_result_best_action)) #display the next best move.
                self.update_text(self.search_result_best_exp_util)
            else:
                self.visualize_state(self.search_root_state) #display the next best move.
        except Exception:
            print(format_exc())
            self.update_status_and_ui(SEARCH_ERROR)

    def restart_game(self, event = None) :
        if self.status in (INITIAL_WAITING,):
            self.current_state = self.initial_state
            self.visualize_state(self.current_state.get_as_root_node())
            self.update_status_and_ui(INITIAL_WAITING)

    def terminate_search_or_discard_results(self, event = None) :
        if self.status in (FINISHED_COMPLETE, FINISHED_INCOMPLETE, FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE_DISP_LEAF, FINISHED_NO_RESULT):
            self.visualize_state(self.search_root_state)
            self.update_status_and_ui(INITIAL_WAITING)
        elif  self.status in (SEARCHING_RUNNING, SEARCHING_PAUSED, SEARCHING_STEP):
            self.update_status_and_ui(TERMINATING_EARLY)


    def fly_blind_search(self, event = None):
        if self.status in (INITIAL_WAITING,):
            # if self.get_agent_selection() in ANYTIME_ALGORITHMS and self.depth_limit_plateau_cutoff_spinbox.get() == "INF":
            #     self.status_text.set("Woah there - don't \"fly blind\" with INF time limit!")
            #     return
            self.start_search(initial_status = SEARCHING_RUNNING, fly_blind = True)

    def toggle_run_pause_or_play_move(self, event = None):
        if self.status in (INITIAL_WAITING,): # Run
            self.start_search(initial_status = SEARCHING_RUNNING)

        elif self.status in (SEARCHING_PAUSED, SEARCHING_STEP) : # Continue
            self.update_status_and_ui(SEARCHING_RUNNING)

        elif self.status in (SEARCHING_RUNNING, ) : # Pause
            self.update_status_and_ui(SEARCHING_PAUSED)

        elif self.status in (FINISHED_INCOMPLETE, FINISHED_COMPLETE, FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE_DISP_LEAF): # Play move
            self.current_state = self.current_state.get_next_state(self.search_result_best_action)
            self.visualize_state(self.current_state.get_as_root_node())
            self.update_status_and_ui(INITIAL_WAITING)

    def step_or_toggle_display_action_leaf(self, event = None):
        if self.status in (INITIAL_WAITING,) : # Run + Step
            self.start_search(initial_status = SEARCHING_PAUSED)

        elif  self.status in (SEARCHING_RUNNING, SEARCHING_PAUSED) : # Step
            self.update_status_and_ui(SEARCHING_STEP)

        elif self.status in (FINISHED_COMPLETE,FINISHED_INCOMPLETE, FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE_DISP_LEAF) : # Display Search Leaf

            goto = {FINISHED_COMPLETE: FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE: FINISHED_INCOMPLETE_DISP_LEAF,
            FINISHED_COMPLETE_DISP_LEAF: FINISHED_COMPLETE, FINISHED_INCOMPLETE_DISP_LEAF : FINISHED_INCOMPLETE}

            self.update_status_and_ui(goto[self.status])

            if self.status in (FINISHED_COMPLETE, FINISHED_INCOMPLETE):
                self.visualize_state(self.search_root_state.get_next_state(self.search_result_best_action)) #display the next best move.
            elif self.status in (FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE_DISP_LEAF):
                self.visualize_state(self.search_result_best_leaf_state) #display the exp path.

    def undo_last_move(self, event = None):
        if self.status in (INITIAL_WAITING,):
            if self.current_state.parent != None:
                self.current_state = self.current_state.parent
                self.visualize_state(self.current_state.get_as_root_node())
                self.update_status_and_ui(INITIAL_WAITING)

    def alg_callback(self, state, cur_value, message=None):
        self.run_pause_button.update()
        self.step_button.update()
        self.reset_button.update()
        self.visualize_callbacks_checkbox.update()
        self.print_status_checkbox.update()

        if self.print_status_state.get():
            self.update_text(cur_value, message)
        if self.visualize_callbacks_state.get() :
            self.visualize_state(state)

        while self.status == SEARCHING_PAUSED :
            time.sleep(.1)
            self.run_pause_button.update()
            self.step_button.update()
            self.reset_button.update()
            self.print_path_states_button.update()


        if self.status == SEARCHING_STEP:
            self.update_status_and_ui(SEARCHING_PAUSED)

        if self.status == SEARCHING_RUNNING :
            time.sleep(float(self.step_time_spinbox.get()))

        return (self.status == TERMINATING_EARLY)

    def alg_callback_blind (self, state, cur_value, message = None):
        return False

    def update_text(self, exp_util, message = None):

        if exp_util != None:
            self.eval_fn_result_text.set('Expected utility of state: {:.4f}'.format(exp_util))
        else :
            self.eval_fn_result_text.set('Expected utility of state: {}'.format(None))

        if message != None:
            self.callback_msg_text.set(message)
        else :
            self.callback_msg_text.set('')


        if type((a := self.current_agent)) in ITERATIVE_SEARCH_AGENTS.values():
            self.counter_text_1.set('This search || Max Depth: {} | Nodes seen: {} | Leaf evals: {}'.format(a.agent.depth_limit, a.agent.total_nodes, a.agent.total_evals))
        elif type(a) in ASSYMETRIC_AGENTS.values():
            self.counter_text_1.set('This search || Rollouts performed: {}'.format(a.agent.total_rollouts))
        elif type(self.current_agent) in SEARCH_AGENTS.values():
            self.counter_text_1.set('This search || Nodes seen: {} | Leaf evals: {}'.format(a.agent.total_nodes, a.agent.total_evals))
        else:
            self.counter_text_1.set("")


    def toggle_display_history(self):
        if self.status == INITIAL_WAITING:
            if self.display_state is self.current_state:
                self.visualize_state(self.current_state.get_as_root_node())
            else:
                self.visualize_state(self.current_state)

    def visualize_state(self, state):
        self.display_state = state
        self.draw_path_to_state()
        self.canvas.update()

    def click_canvas_attempt_action(self, event = None):
        if self.status == INITIAL_WAITING:
            action = self.click_canvas_to_action(event)
            if action in self.current_state.get_all_actions():
                self.current_state = self.current_state.get_next_state(action)
                self.visualize_state(self.current_state.get_as_root_node())
        self.status_text.set(STATUS_TEXT[INITIAL_WAITING].format(self.current_state.current_player_index, 
                                                        self.current_state.player_names[self.current_state.current_player_index],
                                                        self.current_agent_name))


    def draw_path_to_state(self, event = None):
        raise NotImplementedError

    def draw_background(self, event = None):
        raise NotImplementedError

    def click_canvas_to_action(self, event):
        raise NotImplementedError

class RoombaRaceGUI(TestGameGui):
    def __init__(self, master, current_state):
        master.title("Roomba Race Visualizer")
        self.game_class = RoombaRaceGameState
        self.maze_width = current_state.get_width()
        self.maze_height = current_state.get_height()

        self.text_size = MAX_HEIGHT // (self.maze_height * 2)
        super().__init__(master, initial_state, canvas_height = MAX_HEIGHT, canvas_width = MAX_HEIGHT * self.maze_width // self.maze_height, eval_fn_dict = all_fn_dicts[RoombaRaceGameState])

    def calculate_box_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x1 = w * c // self.maze_width
        y1 = h * r // self.maze_height
        x2 = w * (c + 1) // self.maze_width
        y2 = h * (r + 1) // self.maze_height
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x = int(w * (c + .5)) // self.maze_width
        y = int(h * (r + .5)) // self.maze_height
        return (x, y)

    def draw_path_to_state(self, event = None):
        self.canvas.delete('path_line')
        self.canvas.delete('agent')
        self.canvas.delete('cleaned_terrain')

        path = self.display_state.get_path()

        # Draw cleaned terrain
        maze = self.current_state.get_grid()

        for r in range(0,self.maze_height):
            for c in range(0,self.maze_width):
                if maze[r][c] == CLEANED:
                    x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill= COLORS[maze[r][c]], tag='cleaned_terrain')

        for p in range(len(RoombaRaceGameState.player_names)):
            curr_r, curr_c = self.display_state.get_position(p)
            x1, y1, x2, y2 = self.calculate_box_coords(curr_r,curr_c)
            self.canvas.create_oval(x1, y1, x2, y2, fill= COLORS[AGENT[p]], tag='agent')

            path_rc = [state.get_position(p) for state in path]
            path_coords = [self.calculate_center_coords(r,c)
                            for r,c in path_rc]
            if len(path_coords) > 1:
                self.canvas.create_line(path_coords, fill = COLORS[PATH[p]], width = 3, tag='path_line', )


    def draw_background(self, event = None):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas

        # Clear the background grid and terrain
        self.canvas.delete('grid_line')
        self.canvas.delete('terrain_block')

        # Creates all vertical lines
        for c in range(0, self.maze_width):
            x = w * c // self.maze_width
            self.canvas.create_line([(x, 0), (x, h)], tag='grid_line')

        # Creates all horizontal lines
        for r in range(0, self.maze_height):
            y = h * r // self.maze_height
            self.canvas.create_line([(0, y), (w, y)], tag='grid_line')

        # Draw terrain
        maze = self.initial_state.get_grid()
        for r in range(0,self.maze_height):
            for c in range(0,self.maze_width):
                terrain = maze[r][c]
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill= COLORS[terrain], tag='terrain_block')

    def click_canvas_to_action(self, event):
        w = self.canvas.winfo_width() # Get current width of canvas
        col = event.x // (w //  self.maze_width)
        h = self.canvas.winfo_height() # Get current height of canvas
        row = event.y // (h //  self.maze_height)
        # print('clicked {}'.format(col))
        cur_r, cur_c = self.current_state.get_position(self.current_state.current_player_index)
        dr, dc = row - cur_r, col - cur_c
        return RoombaRaceAction(dr, dc)

class TicTacToeGUI(TestGameGui):
    def __init__(self, master, initial_state):
        master.title("Tic-Tac-Toe Search Visualizer")
        self.game_class = TicTacToeGameState
        self.num_rows = TicTacToeGameState.num_rows
        self.num_cols = TicTacToeGameState.num_cols
        self.text_size = MAX_HEIGHT // (self.num_rows * 2)
        self.margin = 5
        super().__init__(master, initial_state, canvas_height = MAX_HEIGHT, canvas_width = MAX_HEIGHT * self.num_cols // self.num_rows , eval_fn_dict = all_fn_dicts[TicTacToeGameState])

    def calculate_box_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x1 = w * c // self.num_cols
        y1 = h * r // self.num_rows
        x2 = w * (c + 1) // self.num_cols
        y2 = h * (r + 1) // self.num_rows
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x = int(w * (c + .5)) // self.num_cols
        y = int(h * (r + .5)) // self.num_rows
        return (x, y)

    def draw_path_to_state(self, event = None):
        self.canvas.delete('numbers')

        self.canvas.delete('pieces')
        self.canvas.delete('numbers')

        # draw pieces
        for r in range(0,self.num_rows):
            for c in range(0,self.num_cols):
                piece = self.display_state.get_piece_at(r,c)
                if piece != TicTacToeGameState.EMPTY:
                    x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                    self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[PIECE[piece]], tag='pieces')

        # draw text for path
        path_coords = [self.calculate_center_coords( *state.last_action ) # r,c coordinates
                        for state in self.display_state.get_path()[1:] ]

        for i, pos in enumerate(path_coords): # don't do the first state
             self.canvas.create_text(pos, fill = COLORS[TEXT], tag = 'numbers',
                 text = str(i+1), font = ('Times New Roman', self.text_size, 'bold' ))

    def draw_background(self, event = None):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        # Clear the background grid frame and empty spots
        self.canvas.delete('grid_line')
        self.canvas.delete('frame')
        self.canvas.delete('empty')

        # Draw all the "frame" - really, background color
        self.canvas.create_rectangle(0, 0, w, h, fill= COLORS[FRAME], tag='frame')

        # Draw all the "empty spots"
        for r in range(0,self.num_rows):
            for c in range(0,self.num_cols):
                piece = self.display_state.get_piece_at(r,c)
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[EMPTY], tag='empty')


        # Creates all vertical lines
        for c in range(0, self.num_cols):
            x = w * c // self.num_cols
            self.canvas.create_line([(x, 0), (x, h)], tag='grid_line', width = 2)

        # Creates all horizontal lines
        for r in range(0, self.num_rows):
            y = h * r // self.num_rows
            self.canvas.create_line([(0, y), (w, y)], tag='grid_line', width = 2)

    def click_canvas_to_action(self, event) -> TicTacToeAction:
        w = self.canvas.winfo_width() # Get current width of canvas
        col = event.x // (w //  self.num_cols)
        h = self.canvas.winfo_height() # Get current height of canvas
        row = event.y // (h //  self.num_rows)
        return TicTacToeAction(row, col)

class NimGUI(TestGameGui):
    def __init__(self, master, initial_state):
        master.title("Nim Search Visualizer")
        self.game_class = NimGameState
        self.num_rows = initial_state.get_num_piles()
        self.num_cols = max(initial_state.get_stones_in_pile(p) for p in range(self.num_rows))
        height = min(MAX_HEIGHT, self.num_rows * 60)
        self.text_size = height // (self.num_rows * 2)
        self.margin = 5
        super().__init__(master, initial_state, canvas_height = height, canvas_width = height * self.num_cols // self.num_rows ,eval_fn_dict = all_fn_dicts[NimGameState])

    def calculate_box_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x1 = w * c // self.num_cols
        y1 = h * r // self.num_rows
        x2 = w * (c + 1) // self.num_cols
        y2 = h * (r + 1) // self.num_rows
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x = int(w * (c + .5)) // self.num_cols
        y = int(h * (r + .5)) // self.num_rows
        return (x, y)

    def draw_path_to_state(self, event = None):
        self.canvas.delete('pieces')
        self.canvas.delete('numbers')
        self.canvas.delete('STONE_pieces')

        # draw pieces
        for r in range(0,self.num_rows):
            for c in range(0,self.display_state.get_stones_in_pile(r)):
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[STONE], tag='pieces')

        # draw text and colored ovals for STONE stones along path

        # for every action taken
        for i, state in enumerate(self.display_state.get_path()[1:]): # don't do the first state
            rem_stones, pile = state.last_action
            orig_stones = state.parent.get_stones_in_pile(pile)
            player = state.parent.current_player_index
            # draw over each stone
            for c in range(orig_stones - rem_stones, orig_stones):
                pos = self.calculate_center_coords(pile,c)
                x1, y1, x2, y2 = self.calculate_box_coords(pile,c)

                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[PIECE[0] if player == 1 else PIECE[1]], tag='STONE_pieces')

                self.canvas.create_text(pos, fill = COLORS[TEXT], tag = 'numbers',
                     text = str(i+1), font = ('Times New Roman', self.text_size, 'bold' ))

    def draw_background(self, event = None):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        # Clear the empty spots
        self.canvas.delete('empty')
        # Draw all the "empty spots"
        for r in range(0,self.num_rows):
            for c in range(0,self.initial_state.get_stones_in_pile(r)):
                pos = self.calculate_center_coords(r,c)
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin,  fill= '', outline = COLORS[STONE], width = 2, dash = (4,4), tag='empty')


    def click_canvas_to_action(self, event) -> NimAction:
        w = self.canvas.winfo_width() # Get current width of canvas
        col = event.x // (w //  self.num_cols)
        h = self.canvas.winfo_height() # Get current height of canvas
        row = event.y // (h //  self.num_rows)
        # print('clicked {}'.format(col))
        pile = row
        rem_stones = self.current_state.get_stones_in_pile(pile) - col
        return NimAction(rem_stones, pile)



class ConnectFourGUI(TestGameGui):
    def __init__(self, master, initial_state):
        master.title("Connect Four Search Visualizer")
        self.game_class = ConnectFourGameState
        self.num_rows = ConnectFourGameState.num_rows
        self.num_cols = ConnectFourGameState.num_cols
        self.text_size = MAX_HEIGHT // (self.num_rows * 2)
        self.margin = MAX_HEIGHT // (self.num_rows * 10)
        super().__init__(master, initial_state, canvas_height = MAX_HEIGHT, canvas_width = MAX_HEIGHT * self.num_cols // self.num_rows, eval_fn_dict = all_fn_dicts[ConnectFourGameState])

    def calculate_box_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x1 = w * c // self.num_cols
        y1 = h * r // self.num_rows
        x2 = w * (c + 1) // self.num_cols
        y2 = h * (r + 1) // self.num_rows
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x = int(w * (c + .5)) // self.num_cols
        y = int(h * (r + .5)) // self.num_rows
        return (x, y)

    def draw_path_to_state(self, event = None):
        self.canvas.delete('numbers')

        self.canvas.delete('pieces')
        self.canvas.delete('numbers')

        # draw pieces
        for r in range(0,self.num_rows):
            for c in range(0,self.num_cols):
                piece = self.display_state.get_piece_at(r,c)
                if piece != ConnectFourGameState.EMPTY:
                    pos = self.calculate_center_coords(r,c)
                    x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                    self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[PIECE[piece]], tag='pieces')

        # draw text for path
        path_coords = [self.calculate_center_coords(
                        self.num_rows -  state.get_column_height(state.last_action.column) ,state.last_action.column ) # r,c coordinates
                        for state in self.display_state.get_path()[1:] ]

        for i, pos in enumerate(path_coords): # don't do the first state
             self.canvas.create_text(pos, fill = COLORS[TEXT], tag = 'numbers',
                 text = str(i+1), font = ('Times New Roman', self.text_size, 'bold' ))

    def draw_background(self, event = None):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        # Clear the background grid frame and empty spots
        self.canvas.delete('grid_line')
        self.canvas.delete('frame')
        self.canvas.delete('empty')

        # Draw all the "frame" - really, background color
        self.canvas.create_rectangle(0, 0, w, h, fill= COLORS[FRAME], tag='frame')

        # Draw all the "empty spots"
        for r in range(0,self.num_rows):
            for c in range(0,self.num_cols):
                piece = self.display_state.get_piece_at(r,c)
                pos = self.calculate_center_coords(r,c)
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[EMPTY], tag='empty')


        # Creates all vertical lines
        for c in range(0, self.num_cols):
            x = w * c // self.num_cols
            self.canvas.create_line([(x, 0), (x, h)], tag='grid_line', width = 2)

        # Creates all horizontal lines
        for r in range(0, self.num_rows):
            y = h * r // self.num_rows
            self.canvas.create_line([(0, y), (w, y)], tag='grid_line', width = 2)


    def click_canvas_to_action(self, event) -> ConnectFourAction:
        w = self.canvas.winfo_width() # Get current width of canvas
        col = event.x // (w //  self.num_cols)
        return ConnectFourAction(col)


GAME_CLASSES_AND_GUIS : Dict[str, Tuple[Type[StateNode], Type[TestGameGui]]] = {
                        'roomba': (RoombaRaceGameState, RoombaRaceGUI),
                        'tictactoe': (TicTacToeGameState,TicTacToeGUI),
                        'connectfour': (ConnectFourGameState, ConnectFourGUI),
                        'nim': (NimGameState, NimGUI)
                        }

if len(argv) < 3 :
    print("Usage:    python lab2_search_gui.py [GAME] [INITIAL_STATE_FILE]")
    print("          GAME can be " + " or ".join("'{}'".format(game) for game in GAME_CLASSES_AND_GUIS))
    print("          INITIAL_STATE_FILE is a path to a text file, OR \"default\"")
    quit()

if (argv[1] not in GAME_CLASSES_AND_GUIS):
    print("1st argument should be one of the following: {}".format(str(list(GAME_CLASSES_AND_GUIS.keys()))))
    quit()


game_class, GUI = GAME_CLASSES_AND_GUIS[argv[1]]
eval_fn_dict = all_fn_dicts[game_class]

initial_state = game_class.defaultInitialState() if argv[2] == 'default' else game_class.readFromFile(argv[2])

root = Tk()

gui = GUI(root, initial_state)

root.mainloop()
