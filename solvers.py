from interpreters import *


def lp_solver_string_based(objective, constraints):
    # Instantiate the solver TODO: refractor the names here
    p = sage.MixedIntegerLinearProgram()
    v = p.new_variable(nonnegative=True, real=True)
    # Objective function is guaranteed to have no inequalities
    ob_fun = 0
    ob_info = determine_coefficients(objective)
    ob_coefficients = ob_info[0]
    maxVarIndex = 0
    varNames = {}  # dictionary so vars in the constraints can match to vars in the objective if the number of vars differs
    for x in range(len(ob_coefficients)):
        ob_fun = ob_fun + ob_coefficients[x] * v[x]
        varNames[ob_info[1][x]] = v[x]
        maxVarIndex = x
    p.set_objective(ob_fun)
    constraints = constraints.strip().split("\n")
    for x in constraints:
        constraintLeft = 0
        constraintRight = 0
        lessThan = False
        greaterThan = False
        equals = False
        parts = []
        if "<=" in x:
            lessThan = True
            parts = x.split("<=")
        elif ">=" in x:
            greaterThan = True
            parts = x.split(">=")
        elif "=" in x:
            equals = True
            parts = x.split("=")
        # left side handling
        cnstLeftInfo = determine_coefficients(parts[0])
        cnstLeftCoefficients = cnstLeftInfo[0]
        for x in range(len(cnstLeftCoefficients)):
            if cnstLeftInfo[1][x] not in varNames:
                varNames[cnstLeftInfo[1][x]] = v[maxVarIndex + 1]
                maxVarIndex += 1
            # print("leftinfo:" + str(cnstLeftInfo[1][x]))
            # print("dictionary:" + str())
            constraintLeft += varNames[cnstLeftInfo[1][x]] * cnstLeftCoefficients[x]
        constraintLeft += get_constant(parts[0])
        # right side handling
        cnstRightInfo = determine_coefficients(parts[1])
        cnstRightCoefficients = cnstRightInfo[0]
        for x in range(len(cnstRightCoefficients)):
            if cnstRightInfo[1][x] not in varNames:
                varNames[cnstRightInfo[1][x]] = v[maxVarIndex + 1]
                maxVarIndex += 1
            constraintRight += varNames[cnstLeftInfo[1][x]] * cnstRightCoefficients[x]
        constraintRight += get_constant(parts[1])
        print(constraintLeft)
        print(constraintRight)
        if lessThan:
            p.add_constraint(constraintLeft <= constraintRight)
        elif greaterThan:
            p.add_constraint(constraintLeft >= constraintRight)
        elif equals:
            p.add_constraint(constraintLeft=constraintRight)
    a = []
    sol = p.solve()
    return [sol, maxVarIndex, varNames, p]


def schedule_project(edges, nodes, beta, crash, name_dict, activities, node_parents, func, func2):
    for x in edges[0]:  # do the edges first so we have the names dictionary
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
        name_dict[a] = func2(a)
        name_dict[b] = func2(b)
    if len(name_dict) + 2 < len(nodes):
        print("Disconnected component")
    for x in nodes:
        info_list = func(x)
        min_time = info_list[0]
        avg_time = info_list[1]
        max_time = info_list[2]
        crash_time = info_list[3]
        crash_cost = info_list[4]

        if crash:
            crash_data = [crash_time, crash_cost]
        else:
            crash_data = None
        if beta:
            beta_data = [min_time, avg_time, max_time]
        else:
            beta_data = avg_time
        activities[x] = Pert(name_dict[x], x, crash_data, beta_data, node_parents[x], name_dict)
    for x in activities:
        activities[x].calc_times(activities)  # need the dictionary for this
    end_nodes = []
    end_nodes_vals = []
    for a in activities:  # Go through all the nodes, find the last ones, save to a list
        if not activities[a].has_children:
            end_nodes.append(a)
            end_nodes_vals.append(activities[a].time_total)
    # Find the latest possible end time to find the expected time of the whole project
    max_time = max(end_nodes_vals)
    # Update this as the end time for each node and let recursion calculate the remaining nodes
    for a in end_nodes:
        print(activities[a].name)
        activities[a].update_end_time(max_time)
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


def max_flow(edges, directional, name_dict, name_get, val_get, start, end):
    edge_string_list = []
    for y in edges:
        for x in y:
            x.update_weight(val_get(x.get_weight_loc()))
            edge_string_list.append(str(x))
            a = x.start_node
            b = x.end_node
            name_dict[a] = name_get(a)
            name_dict[b] = name_get(b)
    if directional:
        G = sage.DiGraph(edge_string_list, weighted=True)
    else:
        G = sage.Graph(edge_string_list, weighted=True)  # TODO: "too many values to unpack" debug this
    x = G.flow(start, end, value_only=False)  # TODO: implement generating the graph from this output
    print(x[0])

