from interpreters import *
from callbacks import *
from simple_graph_callbacks import *
# import dearpygui.dearpygui as dpg #unnecessary as long as
# callbacks has it (callbacks has it to create windows as callbacks
# TODO: manage comments better, especially those describing what methods do
# TODO: continue refractoring until everything is readable
# TODO: read file into visual component, but establish solver objects from read file
# TODO: integrate saving
# TODO: callbacks is getting too large, separate into multiple files
# TODO: comment what is happening before I forgor again
# TODO: find some purpose to the main screen
# TODO: Integrate edge deletion in the simple graph callbacks
# TODO: Change simple graph solvers so it actually outputs on visual screen


def main():
    dpg.create_context()
    with dpg.window(label="Main Menu", width=int(800), height=int(600)):
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Open")
                dpg.add_menu_item(label="Save")
                dpg.add_menu_item(label="Save As")
            with dpg.menu(label="New Solver"):
                dpg.add_menu_item(label="New Linear Program", callback=open_lp)
                dpg.add_menu_item(label="New Max Flow", callback=graph_editor)
                dpg.add_menu_item(label="New PERT/CERN", callback=graph_editor, user_data="PERT")
            with dpg.menu(label="Algorithms"):
                dpg.add_menu_item(label="Symbolic Readers", callback=open_string_readers)
        dpg.add_text("Version: 0.0.1 alpha")
        # with dpg.collapsing_header(label="Widgets"):

        dpg.add_button(label="Save", callback=None)
        dpg.add_input_text(label="string")
        dpg.add_slider_float(label="float")

    dpg.create_viewport(title="window", width=int(825), height=int(800))
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
