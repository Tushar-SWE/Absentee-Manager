import sys
import subprocess
import os
import bcrypt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QApplication
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6 import QtGui

from Registration.create_db import get_user_by_username  # ✅ from Supabase client wrapper


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def show_department_login(callback_on_success):
    class LoginWindow(QWidget):
        def __init__(self):
            super().__init__()

            self.init_ui()
            self.setWindowIcon(QtGui.QIcon(resource_path("assets/APP_logo.ico")))

        def init_ui(self):
            self.setWindowTitle("Department Login")
            self.setMinimumSize(1100, 650)

            # === Stacked Layout with Background ===
            self.main_stack = QVBoxLayout(self)
            self.main_stack.setContentsMargins(0, 0, 0, 0)

            background_label = QLabel(self)
            background_label.setPixmap(QtGui.QPixmap(resource_path("assets/Background.png")))
            background_label.setScaledContents(True)
            background_label.setMinimumSize(1100, 650)

            background_layout = QVBoxLayout(background_label)
            background_layout.setContentsMargins(0, 0, 0, 0)

            # === Foreground Layout ===
            foreground_widget = QWidget()
            foreground_layout = QVBoxLayout(foreground_widget)
            foreground_layout.setContentsMargins(40, 30, 40, 30)

            # === Top bar with logo ===
            top_bar = QHBoxLayout()
            top_bar.addStretch()

            logo = QLabel()
            logo.setPixmap(QtGui.QPixmap(resource_path("assets/logo.png")).scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            logo.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            top_bar.addWidget(logo)

            foreground_layout.addLayout(top_bar)

            # === Center login UI ===
            center_layout = QHBoxLayout()
            center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            content_frame = QFrame()
            content_frame.setMaximumWidth(1000)
            content_frame.setMinimumHeight(550)
            content_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                }
            """)
            content_layout = QHBoxLayout(content_frame)
            content_layout.setContentsMargins(0, 0, 0, 0)

            # === Left Instructions Panel ===
            instructions_panel = QFrame()
            instructions_panel.setMinimumWidth(400)
            instructions_panel.setStyleSheet("""
                background-color: #2563eb;
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            """)
            instructions_layout = QVBoxLayout(instructions_panel)
            instructions_layout.setContentsMargins(30, 25, 30, 25)

            title = QLabel("🏢 Admin Access")
            title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            title.setStyleSheet("color: white;")
            instructions_layout.addWidget(title)

            notes = [
                "Login with your department credentials.",
                "Manage and upload attendance reports.",
                "Trigger automated SMS/Email alerts.",
                "View department-specific dashboards.",
                "Update records anytime securely."
            ]

            for note in notes:
                label = QLabel(f"• {note}")
                label.setWordWrap(True)
                label.setStyleSheet("color: white; font-size: 13px; margin-top: 10px;")
                instructions_layout.addWidget(label)

            instructions_layout.addStretch()
            support = QLabel("")
            support.setStyleSheet("color: white; font-size: 11px; font-style: italic;")
            instructions_layout.addWidget(support)

            # === Right Login Panel ===
            login_panel = QFrame()
            login_panel.setStyleSheet("""
                background-color: white;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            """)
            login_layout = QVBoxLayout(login_panel)
            login_layout.setContentsMargins(40, 30, 40, 30)
            login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the layout

            heading_icon = QLabel("🔐")
            heading_icon.setFont(QFont("Arial", 36))
            heading_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            login_layout.addWidget(heading_icon, alignment=Qt.AlignmentFlag.AlignHCenter)

            heading = QLabel("Department Login")
            heading.setFont(QFont("Arial", 22, QFont.Weight.Bold))
            heading.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            login_layout.addWidget(heading, alignment=Qt.AlignmentFlag.AlignHCenter)

            subtext = QLabel("Authorized access only.")
            subtext.setStyleSheet("color: gray; font-size: 13px;")
            subtext.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            login_layout.addWidget(subtext, alignment=Qt.AlignmentFlag.AlignHCenter)

            login_layout.addSpacing(10)

            self.username_input = self.create_form_input("Username")
            self.password_input = self.create_form_input("Password", is_password=True)

            login_layout.addWidget(self.username_input[0], alignment=Qt.AlignmentFlag.AlignHCenter)
            login_layout.addWidget(self.password_input[0], alignment=Qt.AlignmentFlag.AlignHCenter)

            login_btn = QPushButton("Login to Dashboard")
            login_btn.setFixedSize(350, 45)
            login_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    padding: 10px;
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #1e40af;
                }
            """)
            login_btn.clicked.connect(self.handle_login)
            login_layout.addWidget(login_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

            register_link = QLabel('<a style = "color : #1e40af" href="#">New department? Register here.</a>')
            register_link.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            register_link.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    background: transparent;
                    padding: 0px;
                }
                QLabel::link {
                    color: #1e40af;
                    text-decoration: none;
                }
                QLabel::link:hover {
                    color: #1d4ed8;
                    text-decoration: underline;
                }
            """)
            register_link.setOpenExternalLinks(False)
            register_link.linkActivated.connect(self.open_register_window)
            login_layout.addWidget(register_link, alignment=Qt.AlignmentFlag.AlignHCenter)

            help = QLabel("")
            help.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            help.setStyleSheet("color: #2563eb; font-size: 11px; margin-top: 10px;")
            login_layout.addWidget(help, alignment=Qt.AlignmentFlag.AlignHCenter)
            login_layout.addStretch()

            content_layout.addWidget(instructions_panel)
            content_layout.addWidget(login_panel)

            center_layout.addWidget(content_frame)
            foreground_layout.addLayout(center_layout)

            # === Bottom bar with tagline ===
            bottom_bar = QHBoxLayout()
            tagline = QLabel()
            tagline.setPixmap(QtGui.QPixmap(resource_path("assets/tagline.png")).scaledToHeight(35, Qt.TransformationMode.SmoothTransformation))
            tagline.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
            bottom_bar.addWidget(tagline)
            bottom_bar.addStretch()
            foreground_layout.addLayout(bottom_bar)

            # Add everything
            background_layout.addWidget(foreground_widget)
            self.main_stack.addWidget(background_label)

        def open_register_window(self):
            register_script = os.path.join(os.path.dirname(__file__), "register.py")
            try:
                subprocess.Popen(["python", register_script])
            except Exception as e:
                self.show_message_box("Error", f"Could not open registration window:\n{str(e)}", QMessageBox.Icon.Critical)

        def create_form_input(self, label_text, is_password=False):
            container = QFrame()
            layout = QVBoxLayout(container)
            layout.setSpacing(5)

            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #111; font-weight: bold;")

            input_field = QLineEdit()
            input_field.setFont(QFont("Segoe UI", 10))
            input_field.setFixedSize(350, 45)
            input_field.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: #111;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    padding: 6px;
                }
            """)

            if is_password:
                input_field.setEchoMode(QLineEdit.EchoMode.Password)

            layout.addWidget(label)
            layout.addWidget(input_field)
            container.setLayout(layout)

            return container, input_field

        def show_message_box(self, title, message, icon=QMessageBox.Icon.Information):
            msg_box = QMessageBox(self)
            msg_box.setIcon(icon)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setStyleSheet("QLabel{color:white;} QPushButton{color:white;}")
            msg_box.exec()

        def handle_login(self):
            username = self.username_input[1].text().strip()
            password = self.password_input[1].text().strip()

            if not username or not password:
                self.show_message_box("Error", "Please enter both Username and Password.", QMessageBox.Icon.Critical)
                return

            try:
                user = get_user_by_username(username)
                if not user:
                    self.show_message_box("Login Failed", "❌ User not found.", QMessageBox.Icon.Critical)
                    return

                stored_hash = user["password"]
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    department = user["department"]
                    self.show_message_box("Success", f"✅ Welcome, {department} Department!", QMessageBox.Icon.Information)
                    self.close()
                    callback_on_success(username, department)
                else:
                    self.show_message_box("Login Failed", "❌ Incorrect password.", QMessageBox.Icon.Critical)

            except Exception as e:
                self.show_message_box("Login Failed", f"❌ {str(e)}", QMessageBox.Icon.Critical)

    login_window = LoginWindow()
    login_window.showMaximized()
    return login_window
