from solvers import *
import dearpygui.dearpygui as dpg
import time


def evaluate_lp_string(sender, app_data, user_data):
    a = (lp_solver_string_based(dpg.get_value(user_data[0]), dpg.get_value(user_data[1])))
    with dpg.window(label="LP Solution",width=int(400),height=int(400)):
        dpg.add_text(f"Solution: {a[0]}")
        for x in range(a[1]+1):
            dpg.add_text(f"{list(a[2])[x]}: {a[3].get_values(list(a[2].values())[x])}") #


def open_lp():
    print("New Linear Program")
    with dpg.window(label="LP Solver", pos=(int(100),int(100)), width=int(400), height=int(400)):
        obj_fun = dpg.add_input_text(label="Objective function")
        paragraph = """x>=0\ny>=0\nx<=5\ny<=6"""
        lp_text = dpg.add_input_text(label="\nConstraints", multiline=True, default_value=paragraph, height=int(200),
                                     tab_input=True)
        dpg.add_button(label="Compute", callback=evaluate_lp_string, user_data=[obj_fun, lp_text])
        with dpg.group(horizontal=True):
            dpg.add_checkbox(label="Integer", callback=type_vars_lp)
        dpg.add_radio_button(("Max", "Min"), callback=max_min_lp, horizontal=True)
        # dpg.add_checkbox(label="checkbox" #Availability for more
        dpg.add_text("Currently does not support factored expressions. \nMust be in form ax1 + bx2 + ...")


def open_string_readers(sender, app_data, user_data):
    tagGen = dpg.generate_uuid()
    print(tagGen)
    with dpg.window(label="Input Reading Algorithms", pos=(int(100),int(100)), width=int(400), height=int(400), tag=tagGen):
        function_string = dpg.add_input_text(label="Test Function", default_value="3x+4x^2-3")
        vals = dpg.add_button(label="Run", callback=comp_strs, user_data=[function_string, tagGen])


def comp_strs(sender, app_data, user_data):
    tic_start = time.perf_counter()
    a = determine_coefficients(dpg.get_value(user_data[0]))
    tic_midpoint = time.perf_counter()
    b = str_to_eqs(dpg.get_value(user_data[0]))
    tic_endpoint = time.perf_counter()
    dpg.add_text(f"Algorithm One Read: {tic_midpoint-tic_start:0.4f}", parent=user_data[1])
    dpg.add_text(f"Algorithm Two Read: {tic_endpoint-tic_midpoint:0.4f}", parent=user_data[1])
    dpg.add_text(f"Algorithm One Return: {a}", parent=user_data[1])
    dpg.add_text(f"Algorithm Two Return: {b}", parent=user_data[1])


# def hi():
#     while False:
#         print("Goodbye")
#     else: #Unknown why but if you remove this it breaks
#         print("Hi")


def graph_editor(sender, app_data, user_data):
    """
    TODO: Add support for two finger navigation of the screen for smoother experience
    :param sender:
    :param app_data:
    :param user_data: the type of problem.  Determines what to do
    :return:
    """
    tag_gen = dpg.generate_uuid()
    edges = [[],[]] # A list of two lists, could be a tuple but ah well
    nodes = []
    nodes_inputs = []
    beta_elements = []
    crash_elements = []
    directional = [True]
    crash = [False]
    beta = [False]
    i = 1
    start_node = None

    with dpg.window(label="Graph Editor", pos=(int(100), int(100)), width=int(1000), height=int(1000)):
        with dpg.node_editor(user_data=[edges, user_data, start_node],callback=add_edge,
                             delink_callback=lambda sender, app_data: dpg.delete_item(app_data), minimap=True,
                             minimap_location=dpg.mvNodeMiniMap_Location_BottomRight, menubar=True, tag=tag_gen):
            with dpg.menu_bar():
                dpg.add_menu_item(label="New Node", callback=build_node,
                                  user_data=[tag_gen,1,user_data, nodes, directional, nodes_inputs, beta_elements,
                                             crash_elements, crash, beta])  # TODO: make this look nicer with some sort of container
                dpg.add_menu_item(label="Compute", callback=compute_graph, user_data=[tag_gen, edges, user_data, nodes,
                                                                                      beta, crash])
                if user_data != "PERT":
                    dpg.add_checkbox(label="Directional", callback=make_directional, user_data=[directional, nodes_inputs],
                                     default_value=True)
                else:
                    dpg.add_checkbox(label="Crash", callback=crash_nodes, user_data=[crash, crash_elements])
                    dpg.add_checkbox(label="Beta distributed", callback=beta_nodes, user_data=[beta, beta_elements])
            build_node(None, None, [tag_gen,0,user_data,nodes, directional, nodes_inputs, beta_elements,
                                    crash_elements, crash, beta])

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


def add_predecessor(sender, app_data, user_data):
    tag_gen = user_data
    with dpg.node_attribute(parent=tag_gen) as a:
        with dpg.group(horizontal=True):
            dpg.add_input_text(width=1)
            dpg.add_button(label="Remove", callback=lambda: dpg.delete_item(a))


def make_directional(sender, app_data, user_data):
    fmt = "0"
    if not user_data[0]:
        fmt = "%0.3f"
    for x in user_data[1]:
        #print(x)
        dpg.configure_item(x, readonly=user_data[0], format=fmt)
    user_data[0] = not user_data[0]
    #TODO: now make the solver work with this by adjusting add_edge to split the edges into a list of two lists,
    #the first containing one direction, the other going backwards


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
            user_data[2] = parent_node_2
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


def compute_graph(sender, app_data, user_data):
    parent = user_data[0] #TODO: figure out why we have this
    edges = user_data[1] # list with two lists, basically gotta refigure out why
    type_solver = user_data[2]
    nodes = user_data[3]
    beta = user_data[4][0]
    crash = user_data[5][0]
    name_dict = {}
    activities = {}
    node_parents = {}
    if type_solver == "PERT":
        for x in edges[0]: #do the edges first so we have the names dictionary
            a = x.start_node
            b = x.end_node
            if a in node_parents:
                list_temp = []
                for i in node_parents[a]:
                    list_temp.append(i)
                list_temp.append(b)
                node_parents[a] = list_temp
            else:
                node_parents[a] = [b]
            name_dict[a] = dpg.get_item_label(a)
            name_dict[b] = dpg.get_item_label(b)
        if len(name_dict) +2 < len(nodes):
            print("Disconnected component")
        for x in nodes:
            min_time = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][1])
            max_time = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][3])
            avg_time = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][2])
            crash_time = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][4])
            crash_cost = dpg.get_value(dpg.get_item_children(dpg.get_item_children(x)[1][0])[1][5])
            if crash:
                crash_data = [crash_time, crash_cost]
            else:
                crash_data = None
            if beta:
                beta_data = [min_time, avg_time, max_time]
            else:
                beta_data = avg_time
            activities[x] = Pert(name_dict[x],x,crash_data,beta_data, node_parents[x], name_dict)
        for x in activities:
            activities[x].calc_times(activities) # need the dictionary for this
        end_nodes = []
        end_nodes_vals = []
        for a in activities: # Go through all the nodes, find the last ones, save to a list
            if not activities[a].has_children:
                end_nodes.append(a)
                end_nodes_vals.append(activities[a].time_total)
        # Find the latest possible end time to find the expected time of the whole project
        max_time = max(end_nodes_vals)
        # Update this as the end time for each node and let recursion calculate the remaining nodes
        for a in end_nodes:
            print(activities[a].name)
            activities[a].update_end_time(max_time)
        #Print the nodes
        critical_path = []
        path_variance = 0
        for a in activities:
            if activities[a].is_critical():
                critical_path.append(a)
                path_variance += activities[a].variance
            activities[a].print_info()
            print()
        print(critical_path)
        print(path_variance)
    else: #TODO: integrate this part of the solver
        for y in edges: #for PERT, there is exactly one element y
            for x in y:
                x.update_weight(dpg.get_value(x.get_weight_loc()))
                print(str(x))
                a = x.start_node
                b = x.end_node
                name_dict[a] = dpg.get_item_label(a)
                name_dict[b] = dpg.get_item_label(b)

            # TODO: obtain necessary PERT values and pass them to the interpreter as optional arguments
            # print(str(a) + " " + str(dpg.get_item_label(a))) #second value is indeed the node names.  Use these
            # print(str(b) + " " + str(dpg.get_item_label(b)))
            #Note: if dpg.get_item_children[1] has length one, it is either the start of finish
    #here we have edges (a set of two sets, each containing edges), nodes, names of nodes, and edges
        #TODO: if directional, only consider the first set.  Set by leaving all inputs at 0 from the start and
        # the flow better be 0


#TODO: continue refractoring until everything is readable
#TODO: read file into visual component, but establish solver objects from read file
#TODO: integrate saving

def max_min_lp(sender, app_data):
    None #Here we will need to send information somewhere about whether to max or min


def type_vars_lp(sender, app_data):
    None