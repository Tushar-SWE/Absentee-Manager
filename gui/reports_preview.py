import os
import pandas as pd
import shutil
from PyQt6.QtWidgets import QFileDialog 
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from datetime import datetime

from core.utils import get_month_name
from core.notify import send_notifications_for_department_and_date

# ==== LOCAL REPORTS FOLDER ====
BASE_REPORTS_DIR = "data/absentee_reports"
BASE_Reports_dir_monthly = "data/templates"


def show_report_preview(department, date_str=None):
    if not date_str:
        date_str = datetime.today().strftime("%d.%m.%Y")

    day, month, year = date_str.split(".")
    month_str = get_month_name(int(month))

    # Local department folder
    dept_dir = os.path.join(BASE_REPORTS_DIR, department)
    dept_dir_month = os.path.join(BASE_Reports_dir_monthly, department)

    # Define file names (LOCAL ONLY)
    local_reports = {
        f"{count}-Day Absentees": os.path.join(dept_dir, f"{count}_Consecutive_Absentees_{date_str}.xlsx")
        for count in [3, 6, 10]
    }
    local_reports["New Absentees"] = os.path.join(dept_dir, f"New_Absentees_{date_str}.xlsx")
    local_reports["Monthly Report"] = os.path.join(dept_dir_month, f"Custom_Attendance_Template_{month_str}_{year}.xlsx")

    # Build dialog
    dialog = QDialog()
    dialog.setWindowTitle(f"📁 Absentee Reports")
    dialog.resize(850, 550)

    layout = QVBoxLayout()

    title = QLabel(f"📊 Absentee Reports Preview ({date_str})")
    title.setStyleSheet("font-size: 18px; font-weight: bold;")
    layout.addWidget(title)

    tree = QTreeWidget()
    tree.setHeaderLabels(["Report Type", "Status", "Action"])
    tree.setColumnWidth(0, 250)

    for label, file_path in local_reports.items():
        available = os.path.exists(file_path)
        status = "✅ Available" if available else "❌ Not Found"
        action = "🔍 Preview" if available else "-"
        item = QTreeWidgetItem([label, status, action])
        tree.addTopLevelItem(item)

    tree.itemDoubleClicked.connect(lambda item, _: handle_item_click(item, local_reports))
    layout.addWidget(tree)

    notify_btn = QPushButton("📨 Send Notifications (SMS & Email)")
    notify_btn.setStyleSheet("background-color: #2e7d32; color: white; padding: 10px; font-size: 14px;")
    notify_btn.clicked.connect(lambda: send_notifications(department, date_str))
    layout.addWidget(notify_btn)

    dialog.setLayout(layout)
    dialog.exec()


def handle_item_click(item, local_reports):
    label = item.text(0)
    file_path = local_reports.get(label)

    if not file_path:
        QMessageBox.information(None, "Not Found", "No path mapped for this report.")
        return

    if not os.path.exists(file_path):
        QMessageBox.warning(None, "Missing File", f"The file does not exist:\n{file_path}")
        return

    try:
        # Preview Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        show_excel_preview(df, file_path, label)

    except Exception as e:
        QMessageBox.critical(None, "❌ Error", f"Failed to preview file:\n{str(e)}")


def show_excel_preview(df: pd.DataFrame, file_path: str, title="Excel Preview"):
    dialog = QDialog()
    dialog.setWindowTitle(f"📄 {title}")
    dialog.resize(1000, 600)

    layout = QVBoxLayout()

    file_label = QLabel(file_path)
    file_label.setStyleSheet("color: gray; font-size: 11px;")
    layout.addWidget(file_label)

    table = QTableWidget()
    table.setRowCount(len(df))
    table.setColumnCount(len(df.columns))
    table.setHorizontalHeaderLabels(list(df.columns))

    for row_idx, (_, row) in enumerate(df.iterrows()):
        for col_idx, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_idx, col_idx, item)

    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    download_btn = QPushButton("⬇ Open File")
    download_btn.setStyleSheet("background-color: #1565c0; color: white; padding: 10px; font-size: 13px;")
    download_btn.clicked.connect(lambda: os.startfile(file_path))
    layout.addWidget(download_btn)

    dialog.setLayout(layout)
    dialog.exec()


def send_notifications(department, date_str):
    try:
        results = send_notifications_for_department_and_date(department, date_str)
        QMessageBox.information(None, "✅ Notifications Sent", "\n".join(results))
    except Exception as e:
        QMessageBox.critical(None, "❌ Error", f"Failed to send notifications:\n{e}")
