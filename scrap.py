from sage.all import *
import dearpygui.demo as demo
import dearpygui.dearpygui as dpg
#var('x', 'y')
#print(eval("3*(3*x+2)"))
dpg.create_context()
dpg.create_viewport(title='Custom Title', width=600, height=600)

demo.show_demo()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()


