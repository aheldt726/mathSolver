from solvers import *
import dearpygui.dearpygui as dpg
import time

# Likely to become a file just to create callbacks just to refractor them into their own files later


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






def max_min_lp(sender, app_data):
    None #Here we will need to send information somewhere about whether to max or min


def type_vars_lp(sender, app_data):
    None