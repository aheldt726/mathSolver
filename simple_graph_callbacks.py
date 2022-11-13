from solvers import *
import dearpygui.dearpygui as dpg
import time


def graph_editor(sender, app_data, user_data):
    """
    Opens the GUI node editor, handles PERT/CERN problems as well as max flow
    TODO: Add support for two finger navigation of the screen for smoother experience
    :param sender:
    :param app_data:
    :param user_data: the type of problem.  Determines what to do
    :return:
    """
    # Create variables necessary for handling the simple graphs
    tag_gen = dpg.generate_uuid()  # Needed so we can open multiple windows arbitrarily without problem
    edges = [[], []]  # A list of two lists, could be a tuple but ah well
    # Two lists for the edges so for undirected graphs, we can store half of the edges
    # Idea could be to store multiple weights for a single edge but simpler handling this way
    nodes = []  # Store UUIDs of the nodes in the GUI.  Acts as a simple name and we can snag stuff from it
    nodes_inputs = []  # TODO: figure out what this does
    beta_elements = []  # Stores the graphical elements pertaining to the beta number so we can turn it off
    crash_elements = []  # Same as the beta but for crash elements
    directional = [True]  # Stored as a list so we don't have to go global
    crash = [False]  # Probably could save space just getting whether a particular crash element is visible or not
    beta = [False]
    start_node = [None]  # Here we store a list, first value being the node UUID, second being the checkbox UUID
    end_node = [None]

    with dpg.window(label="Graph Editor", pos=(int(100), int(100)), width=int(1000), height=int(1000)):
        with dpg.node_editor(user_data=[edges, user_data], callback=add_edge,
                             delink_callback=lambda sender, app_data: dpg.delete_item(app_data), minimap=True,
                             minimap_location=dpg.mvNodeMiniMap_Location_BottomRight, menubar=True, tag=tag_gen):
            with dpg.menu_bar():
                dpg.add_menu_item(label="New Node", callback=build_node,
                                  user_data=[tag_gen,1,user_data, nodes, directional, nodes_inputs, beta_elements,
                                             crash_elements, crash, beta, start_node, end_node])  # TODO: make this look nicer with some sort of container
                dpg.add_menu_item(label="Compute", callback=compute_graph, user_data=[directional, edges, user_data, nodes,
                                                                                      beta, crash, start_node, end_node])
                if user_data != "PERT":
                    dpg.add_checkbox(label="Directional", callback=make_directional, user_data=[directional, nodes_inputs],
                                     default_value=True)
                else:  # change this if more simple graphs come about
                    dpg.add_checkbox(label="Crash", callback=crash_nodes, user_data=[crash, crash_elements])
                    dpg.add_checkbox(label="Beta distributed", callback=beta_nodes, user_data=[beta, beta_elements])
            build_node(None, None, [tag_gen,0,user_data,nodes, directional, nodes_inputs, beta_elements,
                                    crash_elements, crash, beta, start_node, end_node])

            if user_data == "PERT":
                with dpg.node(label="Start", pos=[10,200]):
                    with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                        var_none = None  # exists to please IDE
                with dpg.node(label="Finish", pos=[300,200]):
                    with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
                        var_none = None


def crash_nodes(sender, app_data, user_data):
    crash_bool = user_data[0][0]
    crash_data = user_data[1]
    crash_bool = not crash_bool
    user_data[0].pop()
    user_data[0].append(crash_bool)
    for x in crash_data:
        dpg.configure_item(x, enabled=crash_bool, show=crash_bool)


def beta_nodes(sender, app_data, user_data):
    beta_bool = user_data[0][0]
    beta_data = user_data[1]
    beta_bool = not beta_bool
    user_data[0].pop()
    user_data[0].append(beta_bool)
    for x in beta_data:
        dpg.configure_item(x[0], enabled=beta_bool, show=beta_bool)
        dpg.configure_item(x[2], enabled=beta_bool, show=beta_bool)
        if beta_bool:
            dpg.configure_item(x[1], label="Avg Task Time")
        else:
            dpg.configure_item(x[1], label="Task Time")


def build_node(sender, app_data, user_data):
    tag_gen_parent = user_data[0]
    unnecc = user_data[1]  # TODO: resolve this
    graph_type = user_data[2]
    nodes = user_data[3]
    directional = user_data[4]
    nodes_inputs = user_data[5]
    beta_elements = user_data[6]
    crash_elements = user_data[7]
    crash = user_data[8][0]
    beta = user_data[9][0]
    start_node = user_data[10]
    end_node = user_data[11]
    tag_gen = dpg.generate_uuid()
    nodes.append(tag_gen)
    index_fix = 0
    if graph_type == "PERT":
        index_fix = 2
    index = len(dpg.get_item_children(tag_gen_parent)[1])-index_fix
    if index <= 0:
        index = 1
    with dpg.node(label=f"Node {index}", pos=[10, 10], parent=tag_gen_parent, tag=tag_gen):
        if graph_type != "PERT":
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_checkbox(label="Start Node", callback=toggle_node, user_data=[tag_gen, start_node])
                dpg.add_checkbox(label="End Node", callback=toggle_node, user_data=[tag_gen, end_node])
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Add input", callback=add_input_edge, user_data=[tag_gen, directional, nodes_inputs])
                    dpg.add_button(label="Add output", callback=add_output_edge, user_data=[tag_gen])
        else:
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Add earlier task", callback=add_predecessor, user_data=tag_gen)
                    dpg.add_button(label="Add next task", callback=add_successor, user_data=tag_gen)
                minT = dpg.add_input_float(label="Min Task Time", width=100, user_data=tag_gen, enabled=beta,
                                           show=beta, step=1, default_value=1, format="%0.3f")
                avT = dpg.add_input_float(label="Task Time", width=100, user_data=tag_gen, step=1, default_value=1,
                                          format="%0.3f")
                maxT = dpg.add_input_float(label="Max Task Time", width=100, user_data=tag_gen, enabled=beta,
                                           show=beta, step=1, default_value=1, format="%0.3f")
                beta_elements.append([minT, avT, maxT])  # for avT, just change "avg task time" to "task time"
                cT = dpg.add_input_float(label="Crash Time", width=100, user_data=tag_gen, enabled=crash,
                                         show=crash, step=1, default_value=1, format="%0.3f")
                cC = dpg.add_input_float(label="Crash Cost", width=100, user_data=tag_gen, enabled=crash,
                                         show=crash, step=1, default_value=1, format="%0.3f")
                crash_elements.extend([cT, cC])


def toggle_node(sender, app_data, user_data):
    node_id = user_data[0]
    start_node = user_data[1]
    if start_node[0] is not None:
        print(start_node)
        dpg.set_value(start_node[1], False)
        start_node[0] = node_id
        start_node[1] = sender
    else:
        start_node.pop()
        start_node.append(node_id)
        start_node.append(sender)

def add_predecessor(sender, app_data, user_data):
    tag_gen = user_data
    with dpg.node_attribute(parent=tag_gen) as a:
        with dpg.group(horizontal=True):
            dpg.add_input_text(width=1)
            dpg.add_button(label="Remove", callback=lambda: dpg.delete_item(a))


def make_directional(sender, app_data, user_data):
    fmt = "0"
    if not user_data[0][0]:
        fmt = "%0.3f"
    for x in user_data[1]:
        #print(x)
        dpg.configure_item(x, readonly=user_data[0][0], format=fmt)
    user_data[0][0] = not user_data[0][0]
    #TODO: now make the solver work with this by adjusting add_edge to split the edges into a list of two lists,
    #the first containing one direction, the other going backwards
    # TODO: new nodes don't abide by the directional thing, must not be establishing it right


def add_successor(sender, app_data, user_data):
    tag_gen = user_data
    with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, parent=tag_gen) as a:
        with dpg.group(horizontal=True):
            dpg.add_input_text(width=1)
            dpg.add_button(label="Remove", callback=lambda: dpg.delete_item(a))


def add_input_edge(sender, app_data, user_data):
    tag_gen = user_data[0]
    directional = user_data[1]
    nodes_inputs = user_data[2]
    #TODO: suspicious node_input might not be useful
    with dpg.node_attribute(parent=tag_gen) as a:
        with dpg.group(horizontal=True):
            b = dpg.add_input_float(width=85, step=1.0, format="%0.3f", readonly=not directional)
            nodes_inputs.append(b)
            dpg.add_button(label="Remove", callback=lambda: dpg.delete_item(a))


def add_output_edge(sender, app_data, user_data):
    tag_gen = user_data[0]
    with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, parent=tag_gen) as a:
        with dpg.group(horizontal=True):
            dpg.add_input_float(width=85, step=1.0, format="%0.3f")
            dpg.add_button(label="Remove", callback=lambda: dpg.delete_item(a))


def add_edge(sender, app_data, user_data):
    connected_nodes = user_data[0]
    a = dpg.add_node_link(app_data[0], app_data[1], parent=sender)  # we save a just in case we want the id later
    parent_node_1, parent_node_2, w, wloc = None, None, None, None  # solely here to please compiler
    if user_data[1] == "PERT":  # Distinction because PERT doesn't have weights and only needs one set of edges
        # Problem to solve: for every input, there is an identicaloutput, but whichever we exclude will leave some
        # start or finish untouched
        if len(dpg.get_item_children(app_data[0])[1]) != 0:
            # output
            parent_node_1 = dpg.get_item_parent(app_data[1])
            parent_node_2 = dpg.get_item_parent(app_data[0])
            # every edge is going backwards where parent_node_1 comes after parent_node 2
            connected_nodes[0].append(Edge(parent_node_1, parent_node_2, w, wloc))
        elif len(dpg.get_item_children(app_data[1])[1]) != 0:
            # input
            parent_node_1 = dpg.get_item_parent(app_data[1])
            parent_node_2 = dpg.get_item_parent(app_data[0]) #start node always
            connected_nodes[0].append(Edge(parent_node_1, parent_node_2, w, wloc))
    else:
        if len(dpg.get_item_children(app_data[0])[1]) != 0:
            # output
            w = dpg.get_value(dpg.get_item_children(dpg.get_item_children(app_data[0])[1][0])[1][0])
            wloc = dpg.get_item_children(dpg.get_item_children(app_data[0])[1][0])[1][0]
            parent_node_1 = dpg.get_item_parent(app_data[0])
            parent_node_2 = dpg.get_item_parent(app_data[1])
            connected_nodes[0].append(Edge(parent_node_1, parent_node_2, w, wloc))
        if len(dpg.get_item_children(app_data[1])[1]) != 0:
            # input
            w = dpg.get_value(dpg.get_item_children(dpg.get_item_children(app_data[1])[1][0])[1][0])
            wloc = dpg.get_item_children(dpg.get_item_children(app_data[1])[1][0])[1][0]
            parent_node_1 = dpg.get_item_parent(app_data[1])
            parent_node_2 = dpg.get_item_parent(app_data[0])
            connected_nodes[1].append(Edge(parent_node_1, parent_node_2, w, wloc))
        #in interpreter, if w is "", then pert cern


def get_node_info(x):
    """
    Shell method to get GUI information in files that cannot access the GUI
    :param x:
    :return:
    """
    min_time = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][1])
    max_time = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][3])
    avg_time = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][2])
    crash_time = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][4])
    crash_cost = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][5])
    return [min_time, avg_time, max_time, crash_time, crash_cost]


def compute_graph(sender, app_data, user_data):
    """
    Handle the input of graph information, run appropriate solver methods, and display the results in the GUI
    :param sender:
    :param app_data:
    :param user_data:
    :return:
    """
    # Current task: refractor this so solvers are in the solvers tab, this function will
    # update the GUI to display results
    # Name the input values so I can actually understand what is happening
    directional = user_data[0][0]
    edges = user_data[1] # list with two lists, basically gotta refigure out why
    type_solver = user_data[2]
    nodes = user_data[3]
    beta = user_data[4][0]
    crash = user_data[5][0]
    start = user_data[6]
    end = user_data[7]
    name_dict = {}
    activities = {}
    node_parents = {}
    if type_solver == "PERT":
        schedule_project(edges, nodes, beta, crash, name_dict, activities, node_parents, get_node_info,
                         lambda element_id : dpg.get_item_label(element_id))
    else:  # Note: if we find another simple graph (nodes with just integer/float inputs and edges), change this
        max_flow(edges, directional, name_dict, lambda element_id: dpg.get_item_label(element_id), dpg.get_value,
                 start, end)
