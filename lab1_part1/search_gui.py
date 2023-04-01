"""
Visualizing GUI for your solutions to Lab 3.
Use it to test your agents/agents, evaluation functions, and game representations.

Usage:
"""
from __future__ import annotations
from traceback import format_exc
from time import time, sleep
# Tk, Canvas, Frame, Listbox, Button, Checkbutton, IntVar, StringVar, Spinbox, Label
from tkinter import *
from typing import *

from search_problem import StateNode, Action
from search_algorithms import GoalSearchAgent, ALL_AGENTS

INF = float('inf')


class Search_GUI(Tk):
    STEP_TIME_OPTIONS = [str(x) for x in (0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09,
                                          0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 5.0)]

    CUTOFF_OPTIONS: List[str] = [str(x) for x in range(1, 10)] + [str(x) for x in range(
        10, 100, 10)] + [str(x) for x in range(100, 1000, 100)] + ['1000', 'INF']

    def __init__(self, canvas_height: int, canvas_width: int, algorithm_names: Sequence[str], strategy_names: Sequence[str], heuristics: Dict[str, Callable[[StateNode], float]]):
        super().__init__()
        self.heuristics = heuristics

        self.configure(relief='flat', borderwidth=4)

        # Bring to front, but don't keep it there
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)

        # State Visualization Window & Canvas
        self.visual_window = Toplevel(self)
        self.visual_window.title("State Visualization")

        self.canvas = Canvas(
            self.visual_window, height=canvas_height, width=canvas_width, bg='white')
        # grid(row = 0, columnspan = 5) #
        self.canvas.pack(fill=BOTH, expand=True)

        self.visual_window.protocol('WM_DELETE_WINDOW', self.destroy)
        # Bring to front (slightly off from the main window), but don't keep it there.
        self.visual_window.geometry(
            "+%d+%d" % (self.winfo_x(), self.winfo_y()))
        self.visual_window.lift()
        self.visual_window.attributes('-topmost', True)
        self.visual_window.after_idle(
            self.visual_window.attributes, '-topmost', False)

        ###################################################

        # Create widget layout

        self.status_label = Label(
            self, anchor=CENTER, bg="lightblue", pady=3, justify=CENTER, relief=GROOVE)
        self.status_label.grid(row=0, columnspan=3, sticky=N)

        #########################################################################################

        agent_menu_frame = Frame(self, highlightbackground="grey",
                                 highlightthickness=1, relief='flat', borderwidth=3)
        agent_menu_frame.grid(row=1, rowspan=2, column=0, sticky=NW, padx=3)

        Label(agent_menu_frame, text="Core Algorithm:").grid(row=0, sticky=NW)

        # exportselection = 0 ensures that something will always be highlighted
        self.algorithm_listbox = Listbox(
            agent_menu_frame, selectmode=BROWSE, exportselection=0, height=len(algorithm_names))
        self.algorithm_listbox.grid(row=1, sticky=NSEW)
        self.algorithm_listbox.insert(END, *algorithm_names)
        self.algorithm_listbox.config(width=0)  # resize width to contents
        # This sets focus on the first item.
        self.algorithm_listbox.select_set(0)

        Label(agent_menu_frame, text="Search Strategy:").grid(row=2, sticky=NW)

        self.strategy_listbox = Listbox(
            agent_menu_frame, selectmode=BROWSE, exportselection=0, height=len(strategy_names))
        self.strategy_listbox.grid(row=3, sticky=NSEW)
        self.strategy_listbox.insert(END, *strategy_names)
        self.strategy_listbox.config(width=0)
        self.strategy_listbox.select_set(0)

        heuristics_frame = Frame(agent_menu_frame, highlightbackground="lightgrey",
                                 highlightthickness=1, relief='flat', borderwidth=2)
        heuristics_frame.grid(row=4, column=0, sticky=NW, padx=3, pady=3)

        Label(heuristics_frame, text="Cost Heuristic:").grid(row=0, sticky=NW)

        self.heuristic_listbox = Listbox(
            heuristics_frame, selectmode=BROWSE, exportselection=0, height=len(heuristics))
        self.heuristic_listbox.grid(row=3, sticky=NSEW)
        self.heuristic_listbox.insert(END, *heuristics.keys())
        self.heuristic_listbox.config(width=0)
        self.heuristic_listbox.select_set(0)

        #########################################################################################

        controls_frame = Frame(self, highlightbackground="grey",
                               highlightthickness=1, relief='flat', borderwidth=3)
        controls_frame.grid(row=1, column=1, sticky=NW, padx=3)

        cutoffs_frame = Frame(controls_frame)
        cutoffs_frame.grid(row=0, sticky=NW, pady=3)

        cutoff_label = Label(cutoffs_frame, text="Length/Cost Cutoff:")
        cutoff_label.grid(row=0, column=0, sticky=NW)

        self.cutoff_spinbox = Spinbox(cutoffs_frame,
                                      values=Search_GUI.CUTOFF_OPTIONS, width=5, wrap=True)
        self.cutoff_spinbox.grid(row=0, column=1, sticky=NW, padx=5)
        while (self.cutoff_spinbox.get() != "INF"):
            self.cutoff_spinbox.invoke('buttonup')

        self.reset_button = Button(controls_frame, text="Terminate Search",  # End Search early / restart
                                   width=15, pady=3)
        self.reset_button.grid(row=1, column=0, sticky=N)

        self.run_pause_button = Button(controls_frame, text="Start Search",
                                       width=15, pady=3)
        self.run_pause_button.grid(row=2, column=0, sticky=N)

        self.step_button = Button(controls_frame, text="Step (1 Extend)",
                                  width=15, pady=3)
        self.step_button.grid(row=3, column=0, sticky=N)

        self.fly_blind_search_button = Button(controls_frame, text="FLY BLIND",
                                              width=15, pady=3, fg='blue')
        self.fly_blind_search_button.grid(row=4, column=0, sticky=N)

        #########################################################################################

        visual_options_frame = Frame(
            self, width=30, highlightbackground="grey", highlightthickness=1, relief='flat', borderwidth=3)
        visual_options_frame.grid(row=1, column=2, sticky=NW, padx=3)

        self.visualize_state_option_var = IntVar()
        visualize_state_option_checkbox = Checkbutton(
            visual_options_frame, text='Visualize states?', variable=self.visualize_state_option_var, command=self.on_visualize_state_option_click)
        visualize_state_option_checkbox.grid(row=1, column=0, sticky=NW)
        self.visualize_state_option_var.set(1)

        self.print_state_info_option_var = IntVar()
        print_state_info_option_checkbox = Checkbutton(
            visual_options_frame, text='Print state details?', variable=self.print_state_info_option_var, command=self.on_print_state_info_option_click)
        print_state_info_option_checkbox.grid(row=2, column=0, sticky=NW)
        self.print_state_info_option_var.set(1)

        self.analyze_state_option_var = IntVar()
        analyze_state_option_checkbox = Checkbutton(
            visual_options_frame, text='Analyze cost to goal?', variable=self.analyze_state_option_var, command=self.on_analyze_state_option_click)
        analyze_state_option_checkbox.grid(row=3, column=0, sticky=NW)
        self.analyze_state_option_var.set(1)

        self.print_agent_info_option_var = IntVar()
        print_agent_info_option_checkbox = Checkbutton(
            visual_options_frame, text='Print agent counts?', variable=self.print_agent_info_option_var, command=self.on_print_agent_info_option_click)
        print_agent_info_option_checkbox.grid(row=4, column=0, sticky=NW)
        self.print_agent_info_option_var.set(1)

        step_time_spinbox_frame = Frame(visual_options_frame)
        step_time_spinbox_frame.grid(row=5, column=0, sticky=NW)

        step_time_label = Label(step_time_spinbox_frame, text="Step time: ")
        step_time_label.grid(row=0, column=0, sticky=NW)

        self.step_time_spinbox = Spinbox(step_time_spinbox_frame,
                                         values=Search_GUI.STEP_TIME_OPTIONS, format="%3.2f", width=4)
        self.step_time_spinbox.grid(row=0, column=1, sticky=NW)
        while (self.step_time_spinbox.get() != "0.1"):
            self.step_time_spinbox.invoke('buttonup')

        self.history_button = Button(visual_options_frame, text="Print Path",
                                     width=15, pady=3)
        self.history_button.grid(row=6, column=0, sticky=N)

        #########################################################################################

        info_frame = Frame(self, highlightbackground="grey",
                           highlightthickness=1, relief='flat', borderwidth=3)
        info_frame.grid(row=2, column=1, columnspan=2, sticky=NSEW, pady=3)

        self.last_action_label = Label(
            info_frame, fg="darkred", text='Last Action: {}'.format("TBD"), justify=LEFT, anchor=W)
        self.last_action_label.config(font=("Courier", 12))
        self.last_action_label.grid(row=0, sticky=NW)

        self.depth_label = Label(info_frame, fg="green", text='Node Depth: {}'.format(
            "TBD"), justify=LEFT, anchor=W)
        self.depth_label.config(font=("Courier", 12))
        self.depth_label.grid(row=1, sticky=NW)

        self.path_cost_label = Label(
            info_frame, fg="purple", text='Past Cost: {}'.format("TBD"), justify=LEFT, anchor=W)
        self.path_cost_label.config(font=("Courier", 12))
        self.path_cost_label.grid(row=2, sticky=NW)

        self.goal_heuristic_label = Label(
            info_frame, fg="red", justify=LEFT, anchor=W)
        self.goal_heuristic_label.config(font=("Courier", 12))
        self.goal_heuristic_label.grid(row=3, sticky=NW)

        self.agent_info_label_1 = Label(
            info_frame, text='', fg="blue", anchor=CENTER)
        self.agent_info_label_1.grid(row=4, sticky=NW)

        self.agent_info_label_2 = Label(
            info_frame, text='', fg="blue", anchor=CENTER)
        self.agent_info_label_2.grid(row=5, sticky=NW)

        #########################################################################################

    def on_visualize_state_option_click(self):
        self.redraw()

    def on_print_agent_info_option_click(self):
        if not self.print_agent_info_option_var.get():
            self.agent_info_label_1['text'] = ""
            self.agent_info_label_2['text'] = ""

    def on_print_state_info_option_click(self):
        if not self.print_state_info_option_var.get():
            self.last_action_label['text'] = ""
            self.depth_label['text'] = ""
            self.path_cost_label['text'] = ""

    def on_analyze_state_option_click(self):
        if not self.analyze_state_option_var.get():
            self.goal_heuristic_label['text'] = ""

    # Selection access  methods
    def get_step_time(self):
        return float(self.step_time_spinbox.get())

    def get_cutoff(self):
        return float(self.cutoff_spinbox.get())

    def get_algorithm_selection(self) -> str:
        return self.algorithm_listbox.get(self.algorithm_listbox.curselection()[0])

    def get_strategy_selection(self) -> str:
        return self.strategy_listbox.get(self.strategy_listbox.curselection()[0])

    def get_heuristic_selection(self) -> Callable[[StateNode], float]:
        return self.heuristics[self.heuristic_listbox.get(self.heuristic_listbox.curselection()[0])]

    def update_state(self, state: StateNode, please_draw: Optional[bool] = None, please_print: Optional[bool] = None, please_analyze: Optional[bool] = None):
        self.current_state = state
        if please_print is True or (please_print is None and self.print_state_info_option_var.get()):
            self.last_action_label['text'] = "Last Action: {}".format(
                state.describe_last_action())
            self.depth_label['text'] = "Node Depth: {}".format(state.depth)
            self.path_cost_label['text'] = "Path Cost: {:.3f}".format(
                state.path_cost)
        if please_draw is True or (please_draw is None and self.visualize_state_option_var.get()):
            self.draw_state()
        if please_analyze is True or (please_analyze is None and self.analyze_state_option_var.get()):
            self.goal_heuristic_label['text'] = "Est. Rem. Cost to Goal: {}".format(
                self.get_heuristic_selection()(state))

    def update_agent(self, agent: Optional[GoalSearchAgent] = None, please_print: Optional[bool] = None):

        if agent is not None and (please_print is True or (please_print is None and self.print_agent_info_option_var.get())):
            self.agent_info_label_1['text'] = (
                'Total Extends: {}'.format(agent.total_extends))
            self.agent_info_label_2['text'] = (
                'Total Enqueues: {}'.format(agent.total_enqueues))

    def redraw(self):
        if self.visualize_state_option_var.get():
            self.draw_background()
            self.draw_state()
        else:
            self.draw_background()

    # To be overriden by problem-specifc subclasses.
    # Use self.current_state

    def draw_state(self):
        raise NotImplementedError

    def draw_background(self):
        raise NotImplementedError

    def click_canvas_to_action(self, event) -> Action:
        raise NotImplementedError


class Status:
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]) -> bool:
        raise NotImplementedError

    @staticmethod
    def get_status_text(alg: str) -> str:
        raise NotImplementedError

    @staticmethod
    def update_ui(gui: Search_GUI):
        pass

    @staticmethod
    def handle_reset_button(app: Search_GUI_Controller):
        pass

    @staticmethod
    def handle_run_pause_button(app: Search_GUI_Controller):
        pass

    @staticmethod
    def handle_step_button(app: Search_GUI_Controller):
        pass

    @staticmethod
    def handle_fly_blind_search_button(app: Search_GUI_Controller):
        pass

    @staticmethod
    def alg_callback(app: Search_GUI_Controller, node: StateNode) -> bool:
        raise NotImplementedError

    @staticmethod
    def handle_click_canvas(app: Search_GUI_Controller, event=None):
        pass


class Initiating(Status):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status == Initial_Waiting


class Waiting_Base(Status):
    @staticmethod
    def update_ui(gui: Search_GUI):

        gui.history_button['state'] = NORMAL
        gui.history_button['bg'] = 'orchid1'

        gui.reset_button['state'] = NORMAL
        gui.reset_button['text'] = 'Reset to Init St'
        gui.reset_button['bg'] = 'grey'

        # Can choose new algorithm settings
        gui.cutoff_spinbox['state'] = NORMAL

        gui.algorithm_listbox['state'] = NORMAL
        gui.strategy_listbox['state'] = NORMAL
        gui.heuristic_listbox['state'] = NORMAL

        gui.run_pause_button['state'] = NORMAL
        gui.run_pause_button['text'] = 'Start Search'
        gui.run_pause_button['bg'] = 'green'

        gui.step_button['state'] = NORMAL
        gui.step_button['text'] = 'Step (1 Extend)'
        gui.step_button['bg'] = 'yellow'

        gui.fly_blind_search_button['state'] = NORMAL
        gui.fly_blind_search_button['bg'] = 'VioletRed1'

    @staticmethod
    def handle_reset_button(app: Search_GUI_Controller):
        app.gui.update_state(app.initial_state, please_draw=True,
                             please_print=True, please_analyze=True)
        app.update_status_and_ui(Initial_Waiting)

    @staticmethod
    def handle_run_pause_button(app: Search_GUI_Controller):
        app.run_search(Running)

    @staticmethod
    def handle_step_button(app: Search_GUI_Controller):
        app.run_search(Running_Step)

    @staticmethod
    def handle_fly_blind_search_button(app: Search_GUI_Controller):
        app.run_search(Running_Blind)

    @staticmethod
    def handle_click_canvas(app: Search_GUI_Controller, event=None):
        action: Action = app.gui.click_canvas_to_action(event)
        if action is not None and app.gui.current_state.is_legal_action(action):
            app.update_status_and_ui(Interactive_Waiting)
            app.gui.update_state(
                app.gui.current_state.get_next_state(action), please_draw=True)
            # Small hack...
            if app.gui.current_state.is_goal_state():
                app.gui.status_label['text'] += " (Goal state!)"


class Initial_Waiting(Waiting_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Interactive_Waiting, Running, Running_Paused, Running_Step, Running_Blind)

    @staticmethod
    def get_status_text(alg: str):
        return "Pick an agent and search or click to input an action."

    @staticmethod
    def update_ui(gui: Search_GUI):
        Waiting_Base.update_ui(gui)
        gui.reset_button['state'] = DISABLED


class Interactive_Waiting(Waiting_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Initial_Waiting, Running, Running_Paused, Running_Step, Running_Blind)

    @staticmethod
    def get_status_text(alg: str):
        return "Pick an agent and search or click to input an action."

    @staticmethod
    def update_ui(gui: Search_GUI):
        # No need to repeat it all, since coming only from Waiting states
        # Waiting_Base.update_ui(gui)
        gui.reset_button['state'] = NORMAL


class Finished_Success_Waiting(Waiting_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Initial_Waiting, Interactive_Waiting, Running, Running_Paused, Running_Step, Running_Blind)

    @staticmethod
    def get_status_text(alg: str):
        return "{} finished successfully!".format(alg)

    @staticmethod
    def update_ui(gui: Search_GUI):
        Waiting_Base.update_ui(gui)
        gui.run_pause_button['state'] = DISABLED
        gui.step_button['state'] = DISABLED
        gui.fly_blind_search_button['state'] = DISABLED


class Finished_Failure_Waiting(Waiting_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Initial_Waiting, Interactive_Waiting, Running, Running_Paused, Running_Step, Running_Blind)

    @staticmethod
    def get_status_text(alg: str):
        return "{} finished unsuccessfully.".format(alg)

    @staticmethod
    def update_ui(gui: Search_GUI):
        Waiting_Base.update_ui(gui)
        gui.run_pause_button['state'] = DISABLED
        gui.step_button['state'] = DISABLED
        gui.fly_blind_search_button['state'] = DISABLED


class Terminated_Waiting(Waiting_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Initial_Waiting, Interactive_Waiting, Running, Running_Paused, Running_Step, Running_Blind)

    @staticmethod
    def get_status_text(alg: str):
        return "{} was terminated early.".format(alg)


class Running_Base(Status):
    @staticmethod
    def update_ui(gui: Search_GUI):
        gui.reset_button['state'] = NORMAL
        gui.reset_button['text'] = 'Terminate Search'
        gui.reset_button['bg'] = 'red'

        gui.cutoff_spinbox['state'] = "readonly"

        # Cannot choose new algorithm settings during execution, give at least visual indication
        gui.algorithm_listbox['state'] = DISABLED
        gui.strategy_listbox['state'] = DISABLED
        gui.heuristic_listbox['state'] = DISABLED

        gui.step_button['text'] = 'Step (1 Extend)'
        gui.step_button['bg'] = 'yellow'
        # Specifics about the run_pause and step button in actual statuses

        gui.fly_blind_search_button['state'] = DISABLED
        gui.fly_blind_search_button['bg'] = 'grey'

    @staticmethod
    def handle_reset_button(app: Search_GUI_Controller):
        app.update_status_and_ui(Running_Terminating)

    @staticmethod
    def alg_callback(app: Search_GUI_Controller, node: StateNode) -> bool:
        app.gui.update_state(node)
        app.gui.update_agent(app.current_agent)
        app.gui.update_idletasks()
        app.sleep_update_tk(app.gui.get_step_time())
        return False


class Running(Running_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Running_Paused, Running_Step, Running_Blind,
                               Running_Terminating, Finished_Success_Waiting, Finished_Failure_Waiting, Algorithm_Error)

    @staticmethod
    def get_status_text(alg: str):
        return "{} is running...".format(alg),

    @staticmethod
    def update_ui(gui: Search_GUI):
        Running_Base.update_ui(gui)

        gui.step_button['state'] = NORMAL

        gui.run_pause_button['state'] = NORMAL
        gui.run_pause_button['text'] = 'Pause Search'
        gui.run_pause_button['bg'] = 'orange'

    @staticmethod
    def handle_run_pause_button(app: Search_GUI_Controller):
        app.update_status_and_ui(Running_Paused)

    @staticmethod
    def handle_step_button(app: Search_GUI_Controller):
        app.update_status_and_ui(Running_Step)

    @staticmethod
    def handle_fly_blind_search_button(app: Search_GUI_Controller):
        app.update_status_and_ui(Running_Blind)


class Running_Step(Running_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Running_Paused, Running, Running_Blind,
                               Running_Terminating, Finished_Success_Waiting, Finished_Failure_Waiting, Algorithm_Error)

    @staticmethod
    def get_status_text(alg: str):
        return "{} is taking one step...".format(alg),

    @staticmethod
    def update_ui(gui: Search_GUI):
        Running_Base.update_ui(gui)

        gui.run_pause_button['state'] = NORMAL
        gui.run_pause_button['text'] = 'Continue Search'
        gui.run_pause_button['bg'] = 'green'

        gui.step_button['state'] = DISABLED

    @staticmethod
    def handle_run_pause_button(app: Search_GUI_Controller):
        app.update_status_and_ui(Running)

    @staticmethod
    def handle_fly_blind_search_button(app: Search_GUI_Controller):
        app.update_status_and_ui(Running_Blind)

    @staticmethod
    def alg_callback(app: Search_GUI_Controller, node: StateNode) -> bool:
        # Definitely want to see the info if we step...
        app.gui.update_state(node, please_print=True,
                             please_draw=True, please_analyze=True)
        app.gui.update_agent(app.current_agent, please_print=True)
        app.gui.update_idletasks()
        app.sleep_update_tk(app.gui.get_step_time())

        app.update_status_and_ui(Running_Paused)
        while app.status == Running_Paused:
            app.sleep_update_tk(.25)  # Wait until status changes
        return False


class Running_Paused(Running_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Running_Step, Running, Running_Blind,
                               Running_Terminating, Finished_Success_Waiting, Finished_Failure_Waiting, Algorithm_Error)

    @staticmethod
    def get_status_text(alg: str):
        return "{} is paused.".format(alg),

    @staticmethod
    def update_ui(gui: Search_GUI):
        # Since only coming from Running_Active and Running_Steo, no need to update everything
        # Running_Base.update_ui(gui)

        gui.run_pause_button['state'] = NORMAL
        gui.run_pause_button['text'] = 'Continue Search'
        gui.run_pause_button['bg'] = 'green'

        gui.step_button['state'] = NORMAL

    @staticmethod
    def handle_run_pause_button(app: Search_GUI_Controller):
        app.update_status_and_ui(Running)

    @staticmethod
    def handle_step_button(app: Search_GUI_Controller):
        app.update_status_and_ui(Running_Step)

    @staticmethod
    def handle_fly_blind_search_button(app: Search_GUI_Controller):
        app.update_status_and_ui(Running_Blind)

    @staticmethod
    def alg_callback(app: Search_GUI_Controller, node: StateNode) -> bool:
        while app.status == Running_Paused:
            app.sleep_update_tk(.25)  # Wait until status changes
        # Run whatever the new status' callback is, ultimately
        return app.status.alg_callback(app, node)


class Running_Blind(Running_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Finished_Success_Waiting, Finished_Failure_Waiting, Algorithm_Error)

    @staticmethod
    def get_status_text(alg: str):
        return "{} is running to completion (be patient)...".format(alg)

    @staticmethod
    def update_ui(gui: Search_GUI):
        Running_Base.update_ui(gui)
        gui.reset_button['state'] = DISABLED
        gui.run_pause_button['state'] = DISABLED
        gui.step_button['state'] = DISABLED
        gui.fly_blind_search_button['state'] = DISABLED

    @staticmethod
    def alg_callback(app: Search_GUI_Controller, node: StateNode) -> bool:
        return False


class Running_Terminating(Running_Base):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return next_status in (Terminated_Waiting, Algorithm_Error, Finished_Failure_Waiting, Finished_Success_Waiting)

    @staticmethod
    def get_status_text(alg: str):
        return "{} is terminating early...".format(alg)

    @staticmethod
    def update_ui(gui: Search_GUI):
        gui.reset_button['state'] = DISABLED
        gui.run_pause_button['state'] = DISABLED
        gui.step_button['state'] = DISABLED
        gui.fly_blind_search_button['state'] = DISABLED

    @staticmethod
    def alg_callback(app: Search_GUI_Controller, node: StateNode) -> bool:
        Running_Base.alg_callback(app, node)
        return True


class Algorithm_Error(Status):
    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return False

    @staticmethod
    def get_status_text(alg: str):
        return "Error while running algorithm!"

    @staticmethod
    def update_ui(gui: Search_GUI):
        gui.reset_button['state'] = DISABLED
        gui.run_pause_button['state'] = DISABLED
        gui.step_button['state'] = DISABLED
        gui.fly_blind_search_button['state'] = DISABLED


class Status_Transition_Error(Status):

    from_status: Optional[Type[Status]] = None
    to_status: Optional[Type[Status]] = None

    @staticmethod
    def is_valid_transition_to(next_status: Type[Status]):
        return False

    @staticmethod
    def get_status_text(alg: str):
        return "Unexpected transition from {} to {}".format(Status_Transition_Error.from_status,
                                                            Status_Transition_Error.to_status)

    @staticmethod
    def update_ui(gui: Search_GUI):
        gui.reset_button['state'] = DISABLED
        gui.run_pause_button['state'] = DISABLED
        gui.step_button['state'] = DISABLED
        gui.fly_blind_search_button['state'] = DISABLED


class Search_GUI_Controller:
    gui: Search_GUI
    initial_state: StateNode
    status: Type[Status]
    current_agent: Optional[GoalSearchAgent]
    heuristics: Dict[str, Callable[[StateNode], float]]

    def __init__(self, gui: Search_GUI, initial_state: StateNode, heuristics: Dict[str, Callable[[StateNode], float]], all_agents: Dict[str, Dict[str, Type[GoalSearchAgent]]] = ALL_AGENTS):
        self.gui = gui
        self.all_agents = all_agents
        self.initial_state = initial_state
        self.heuristics = heuristics
        self.gui.update_state(initial_state, please_draw=True,
                              please_print=True, please_analyze=False)
        self.bind_commands_to_gui()

        self.current_agent = None

        self.status = Initiating
        self.update_status_and_ui(Initial_Waiting)

    def bind_commands_to_gui(self):
        self.gui.canvas.bind('<Configure>', lambda *args: self.gui.redraw())
        self.gui.canvas.bind(
            '<Button-1>', lambda e: self.status.handle_click_canvas(self, e))
        self.gui.history_button['command'] = lambda: self.handle_history_button(
        )

        # Status-dependent commands
        self.gui.reset_button['command'] = lambda: self.status.handle_reset_button(
            self)
        self.gui.fly_blind_search_button['command'] = lambda: self.status.handle_fly_blind_search_button(
            self)
        self.gui.run_pause_button['command'] = lambda: self.status.handle_run_pause_button(
            self)
        self.gui.step_button['command'] = lambda: self.status.handle_step_button(
            self)

    def update_status_and_ui(self, newstatus: Type[Status]):
        if self.status is newstatus:
            return
        if newstatus is Algorithm_Error or self.status.is_valid_transition_to(newstatus):
            self.status = newstatus
        else:
            Status_Transition_Error.to_status = newstatus
            Status_Transition_Error.from_status = self.status
            self.status = Status_Transition_Error
        self.gui.status_label['text'] = self.status.get_status_text(
            type(self.current_agent).__name__ if self.current_agent != None else "NO ALG")
        self.status.update_ui(self.gui)
        self.gui.update_idletasks()

    def verify_and_update_parameters(self, nextstatus: Type[Status]) -> bool:
        try:
            cutoff = self.gui.get_cutoff()
            if nextstatus == Running_Blind and (cutoff == INF):
                self.gui.status_label['text'] = (
                    "Don't do a blind search without depth/cost limits!")
                return False
        except Exception:
            self.gui.status_label['text'] = (
                "Cutoff is not a valid number. ('INF' for no limit)")
            return False
        return True

    def get_agent_selection(self) -> GoalSearchAgent:
        alg = self.gui.get_algorithm_selection()
        strat = self.gui.get_strategy_selection()
        agent_class = self.all_agents[alg][strat]
        return agent_class(heuristic=self.gui.get_heuristic_selection())

    def run_search(self, status: Type[Running_Base]):
        if not self.verify_and_update_parameters(status):
            return

        self.current_agent = self.get_agent_selection()
        self.update_status_and_ui(status)
        try:
            start_time = time()
            solution_state: Optional[StateNode] = self.current_agent.search(initial_state=self.gui.current_state.get_as_root_node(),
                                                                            gui_callback_fn=self.alg_callback,
                                                                            cutoff=self.gui.get_cutoff())
            elapsed_time = time() - start_time

            print("{} ran for {:.4f} seconds.".format(
                type(self.current_agent).__name__, elapsed_time))

            self.gui.update_agent(self.current_agent, please_print=True)
            if solution_state is not None:
                self.gui.update_state(
                    solution_state, please_draw=True, please_print=True, please_analyze=True)
                if solution_state.is_goal_state():
                    self.update_status_and_ui(Finished_Success_Waiting)
                else:
                    self.update_status_and_ui(Finished_Failure_Waiting)
            else:
                self.gui.update_state(
                    self.initial_state, please_draw=True, please_print=True, please_analyze=True)
                if self.status is Running_Terminating:
                    self.update_status_and_ui(Terminated_Waiting)
                else:
                    self.update_status_and_ui(Finished_Failure_Waiting)

            self.sleep_update_tk(.1)
        except Exception:
            print(format_exc())
            if self.status != Status_Transition_Error:
                self.update_status_and_ui(Algorithm_Error)

    def sleep_update_tk(self, secs: float, interval: float = .05):
        '''
        Sleep for a time while continuing to update the tkinter gui.
        '''
        try:
            self.gui.update()
            t = 0.0
            while t < secs:
                sleep(interval)
                self.gui.update()
                t += interval
        except TclError as e:
            if "application has been destroyed" not in e.args[0]:
                raise

    def alg_callback(self, node: StateNode) -> bool:
        return self.status.alg_callback(self, node)

    def handle_history_button(self):
        path = self.gui.current_state.get_path()

        # TODO radio button choice for actions only or states + actions
        print(path[0])
        print()
        for node in path[1:]:
            print("({}): {} [Cost: {}]".format(node.depth,
                  node.describe_last_action(), node.path_cost))
            print()
            # TODO radio button choice for actions only or states + actions
            print(str(node))
            print()
