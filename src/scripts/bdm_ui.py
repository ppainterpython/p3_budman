print("Starting BudMan GUI Application...")
import time
st = time.time()
print(f"  Initial setup time: {time.time() -st:.3f} seconds.")
from p3_utils.p3_app_timing import APP_START_TIME
import p3_utils as p3u, p3logging as p3l, p3_mvvm as p3m
from budman_gui_view  import BudManGUIView
it = time.time() -st
print(f"  Imports completed in {it:.3f} seconds.")

if __name__ == "__main__":
    print(f"  Time since app start: {p3u.elapsed_timer_str(APP_START_TIME)}")
    gui_app: BudManGUIView = BudManGUIView()
    print(f"  GUI setup time: {p3u.elapsed_timer_str(APP_START_TIME)}")
    gui_app.initialize()
    print(f"  GUI initialized in: {p3u.elapsed_timer_str(APP_START_TIME)}")
    gui_app.root.load_sample_data()
    print(f"  Sample data loaded in: {p3u.elapsed_timer_str(APP_START_TIME)}")
    print(f"Running BudMan GUI Application...")
    cmd_result: p3m.CMD_RESULT_TYPE = None
    cmd_result = gui_app.run()
    print(f"Application finished with result: {cmd_result}")
    