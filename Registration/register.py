# register.py (PyQt6 version)

import sys
import bcrypt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton,
    QVBoxLayout, QFormLayout, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from create_db import insert_user  # Supabase insert method

class DepartmentRegistration(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Department Registration")
        self.setMinimumSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Register Department")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.confirm_input = QLineEdit()
        self.department_input = QComboBox()
        self.department_input.addItems([
            "Select Department", "BIW", "Engine", "Paint", "TCF", "Quality", "Logistics"
        ])

        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Username:", self.username_input)
        form.addRow("Password:", self.password_input)
        form.addRow("Confirm Password:", self.confirm_input)
        form.addRow("Department:", self.department_input)

        layout.addLayout(form)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register_user)
        layout.addWidget(self.register_btn)

        note = QLabel("Already registered? Close this window and login.")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(note)

        self.setLayout(layout)

    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()
        department = self.department_input.currentText()

        if not username or not password or not confirm or department == "Select Department":
            QMessageBox.warning(self, "Incomplete", "All fields are required.")
            return

        if password != confirm:
            QMessageBox.critical(self, "Mismatch", "Passwords do not match.")
            return

        try:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            insert_user(username, password_hash, department)
            QMessageBox.information(self, "Success", f"✅ Department '{department}' registered successfully.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Registration failed:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DepartmentRegistration()
    window.show()
    sys.exit(app.exec())
