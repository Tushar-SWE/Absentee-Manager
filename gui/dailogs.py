from PyQt6.QtWidgets import (
    QMessageBox, QInputDialog, QApplication, QWidget
)
from PyQt6.QtCore import Qt
import sys

# Ensure QApplication exists only once
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# A visible but minimal reusable dialog parent
class HiddenDialogParent(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1, 1)
        self.setWindowFlags(self.windowFlags() | 
                            Qt.WindowType.Tool | 
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.hide()

# Create a single shared parent
_dialog_parent = HiddenDialogParent()

def _get_parent():
    return _dialog_parent


def confirm_action(message="Are you sure?"):
    """❓ Ask for confirmation before proceeding"""
    result = QMessageBox.question(
        _get_parent(),
        "Confirm",
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return result == QMessageBox.StandardButton.Yes


def alert_success(message):
    """✅ Show a success message"""
    QMessageBox.information(_get_parent(), "Success", message)


def alert_error(message):
    """❌ Show an error message"""
    QMessageBox.critical(_get_parent(), "Error", message)


def alert_warning(message):
    """⚠️ Show a warning dialog"""
    QMessageBox.warning(_get_parent(), "Warning", message)


def ask_text_input(prompt, title="Input Required"):
    """✍️ Prompt user for single-line text input"""
    text, ok = QInputDialog.getText(_get_parent(), title, prompt)
    return text if ok else None
