# main.py
from Registration.login import show_department_login
from gui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)  # ✅ Create QApplication only once

login_window = None  # Keep global reference
main_window = None

def on_login_success(username, dept_name):
    global main_window
    main_window = MainWindow(dept_name, username, login_callback=start_login)
    main_window.show()

def start_login():
    global login_window
    login_window = show_department_login(on_login_success)  # ✅ Capture and persist login window reference

if __name__ == "__main__":
    start_login()
    sys.exit(app.exec())  # ✅ Start Qt event loop once
