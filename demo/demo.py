try:
    import tkinter
except ImportError:
    import Tkinter as tkinter
# hsmpy is Hierarchical State Machine implementation for Python
# it's used here to implement GUI logic
import quadpy
from quadpy.rectangle import Rectangle
from hsmpy import HSM, State, T, Initial, Internal, Choice, EventBus, Event


# you can enable logging to see what's going on under the hood of HSM
#import logging
#logging.basicConfig(level=logging.DEBUG)


# tool aliases
Selection_tool, Drawing_tool = ('Select', 'Draw')

# eventbus will be used for all events
# Tkinter events will also be routed through it
eb = EventBus()


# HSM events
class Tool_Changed(Event): pass
class Mouse_Event(Event):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.data = (x, y)
class Canvas_Up(Mouse_Event): pass
class Canvas_Down(Mouse_Event): pass
class Canvas_Move(Mouse_Event): pass


# create Tkinter GUI
root = tkinter.Tk()
canvas = tkinter.Canvas(width=700, height=700,
                        highlightthickness=0, background='white')
canvas.pack(fill='both', expand=True, padx=6, pady=6)

frame = tkinter.Frame()
labels = []
for i, tool in enumerate([Selection_tool, Drawing_tool]):
    lbl = tkinter.Label(frame, text=tool, width=8, relief='raised')
    wtf = tool

    def get_closure(for_tool):
        return lambda _: eb.dispatch(Tool_Changed(for_tool))
    lbl.bind('<Button-1>', get_closure(tool))
    lbl.pack(padx=6, pady=6 * (i % 2))
    labels.append(lbl)
frame.pack(side='left', fill='y', expand=True, pady=6)

canvas.bind('<Button-1>', lambda e: eb.dispatch(Canvas_Down(e.x, e.y)))
canvas.bind('<B1-Motion>', lambda e: eb.dispatch(Canvas_Move(e.x, e.y)))
canvas.bind('<ButtonRelease-1>', lambda e: eb.dispatch(Canvas_Up(e.x, e.y)))



# I'll just put these here and reference them directly later, for simplicity
quad = quadpy.Node(0, 0, 700, 700, max_depth=9)
selected_elems = []
canvas_grid = {}  # quadtree grid, mapping: bounds -> tkinter rectangle id




##### HSM state and transition actions #####


def update_chosen_tool(evt, hsm):
    for lbl in labels:
        lbl['relief'] = 'sunken' if evt.data == lbl['text'] else 'raised'
    hsm.data.canvas_tool = evt.data


# quadtree grid visualization:

def update_grid():
    updated_bounds = set(quad._get_grid_bounds())
    current_bounds = set(canvas_grid.keys())
    deleted = current_bounds.difference(updated_bounds)
    added = updated_bounds.difference(current_bounds)
    for d in deleted:
        canvas.delete(canvas_grid[d])
        del canvas_grid[d]
    for a in added:
        added_id = canvas.create_rectangle(a, outline='grey')
        canvas_grid[a] = added_id


# drawing new rectangle:

def initialize_rectangle(evt, hsm):
    x, y = evt.data
    bounds = (x, y, x + 1, y + 1)
    rect = Rectangle(*bounds)
    rect.canvas_id = canvas.create_rectangle(bounds, outline='blue')
    hsm.data.canvas_temp_data = (x, y, rect)
    quad.insert(rect)
    update_grid()


def draw_rectangle(evt, hsm):
    x, y, rect = hsm.data.canvas_temp_data
    bounds = (x, y, evt.x, evt.y)
    rect.bounds = bounds
    canvas.coords(rect.canvas_id, bounds)
    quad.reinsert(rect)
    update_grid()


# selecting and moving:

def elems_under_cursor(evt, hsm):
    return quad.get_children_under_point(evt.x, evt.y)


def select_elems(elems):
    global selected_elems
    [canvas.itemconfig(e.canvas_id, outline='blue') for e, _ in selected_elems]
    selected_elems = [(el, el.bounds) for el in elems]
    [canvas.itemconfig(e.canvas_id, outline='red') for e, _ in selected_elems]


def select_under_cursor(evt, hsm):
    hsm.data.moving_start = (evt.x, evt.y)
    elems = elems_under_cursor(evt, hsm)
    if not elems:
        assert False, "this cannot happen"
    just_elems = set(el for el, _ in selected_elems)
    if not any(el in just_elems for el in elems):
        # clicked non-selected element, select it
        select_elems([elems[0]])
    else:
        # hack to refresh initial bounds for each tuple in selected_elems
        select_elems([el for el, _ in selected_elems])


def move_elements(evt, hsm):
    x, y = hsm.data.moving_start
    off_x, off_y = evt.x - x, evt.y - y
    for el, original_bounds in selected_elems:
        x1, y1, x2, y2 = original_bounds
        el.bounds = (x1 + off_x, y1 + off_y, x2 + off_x, y2 + off_y)
        canvas.coords(el.canvas_id, el.bounds)
        quad.reinsert(el)
    update_grid()


# selection marquee

def create_marquee_rect(evt, hsm):
    rect_id = canvas.create_rectangle((evt.x, evt.y, evt.x, evt.y),
                                      outline='orange')
    hsm.data.canvas_marquee = (evt.x, evt.y, rect_id)
    select_elems([])


def drag_marquee_rect(evt, hsm):
    x, y, rect_id = hsm.data.canvas_marquee
    bounds = (x, y, evt.x, evt.y)
    select_elems(quad.get_overlapped_children(bounds))
    canvas.coords(rect_id, bounds)


def clear_marquee_rect(evt, hsm):
    _, _, rect_id = hsm.data.canvas_marquee
    canvas.delete(rect_id)


# define HSM state structure and transitions between states:

states = {
    'app': State({
        'select_tool_chosen': State({
            'select_tool_hovering': State(),
            'dragging_marquee': State(on_enter=create_marquee_rect,
                                      on_exit=clear_marquee_rect),
            'moving_elements': State(on_enter=select_under_cursor),
        }),
        'draw_tool_chosen': State({
            'draw_tool_hovering': State(),
            'drawing': State(),
        })
    })
}

transitions = {
    'app': {
        Initial: T('draw_tool_chosen'),
        Tool_Changed: Choice({
            Selection_tool: 'select_tool_chosen',
            Drawing_tool: 'draw_tool_chosen' },
            default='select_tool_chosen',
            action=update_chosen_tool)
    },
    'select_tool_chosen': {
        Initial: T('select_tool_hovering'),
        Canvas_Up: T('select_tool_hovering'),
    },
    ####
    'select_tool_hovering': {
        Canvas_Down: Choice({
            False: 'dragging_marquee',
            True: 'moving_elements', },
            default='dragging_marquee',
            key=lambda e, h: len(elems_under_cursor(e, h)) > 0),
    },
    'dragging_marquee': {
        Canvas_Move: Internal(action=drag_marquee_rect),
    },
    'moving_elements': {
        Canvas_Move: Internal(action=move_elements),
    },
    ###
    'draw_tool_chosen': {
        Initial: T('draw_tool_hovering'),
        Canvas_Up: T('draw_tool_hovering'),
    },
    'draw_tool_hovering': {
        Canvas_Down: T('drawing', action=initialize_rectangle),
    },
    'drawing': {
        Canvas_Move: Internal(action=draw_rectangle),
    },
}


# initialize HSM with defined states and transitions and run

hsm = HSM(states, transitions)
hsm.start(eb)
eb.dispatch(Tool_Changed(Drawing_tool))

root.mainloop()
