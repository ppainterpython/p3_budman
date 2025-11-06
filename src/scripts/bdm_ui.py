import p3_utils as p3u, p3logging as p3l, p3_mvvm as p3m
from budman_gui_view  import BudManGUIView

if __name__ == "__main__":
    gui_app: BudManGUIView = BudManGUIView()
    cmd_result: p3m.CMD_RESULT_TYPE = None
    cmd_result = gui_app.run()
    print(f"Application finished with result: {cmd_result}")
    