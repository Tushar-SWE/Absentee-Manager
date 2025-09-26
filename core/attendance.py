# gui/attendance_updater.py

import os
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.utils import is_valid_date, preprocess_sundays
from core.reports import generate_absent_reports


class AttendanceUpdater(QWidget):
    def __init__(self, department, parent=None):
        super().__init__(parent)
        self.department = department
        self.setWindowTitle("Attendance Updater")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("📤 Update Daily Attendance")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.template_path = ""
        self.attendance_path = ""
        self.selected_date = ""

        self.template_btn = QPushButton("📁 Choose Monthly Template")
        self.template_btn.clicked.connect(self.select_template)
        layout.addWidget(self.template_btn)

        self.attendance_btn = QPushButton("📂 Choose Daily Attendance File")
        self.attendance_btn.clicked.connect(self.select_attendance)
        layout.addWidget(self.attendance_btn)

        self.date_combo = QComboBox()
        self.date_combo.setPlaceholderText("📅 Select Attendance Date (from template)")
        layout.addWidget(self.date_combo)

        self.update_btn = QPushButton("✅ Update Attendance")
        self.update_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        self.update_btn.clicked.connect(self.update_attendance)
        layout.addWidget(self.update_btn)

    def select_template(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Monthly Template", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.template_path = file_path
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
                self.date_combo.clear()
                date_columns = [col for col in df.columns if is_valid_date(col)]
                self.date_combo.addItems(date_columns)
                QMessageBox.information(self, "Template Loaded", f"Loaded {len(date_columns)} date columns.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load template:\n{e}")

    def select_attendance(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Daily Attendance", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.attendance_path = file_path
            QMessageBox.information(self, "Attendance Selected", f"Selected: {file_path}")

    def update_attendance(self):
        if not self.template_path or not self.attendance_path:
            QMessageBox.warning(self, "Missing File", "Please select both template and attendance files.")
            return

        date_column = self.date_combo.currentText()
        if not date_column:
            QMessageBox.warning(self, "No Date Selected", "Please select a valid attendance date from the dropdown.")
            return

        try:
            df_template = pd.read_excel(self.template_path, engine='openpyxl')
            df_attendance = pd.read_excel(self.attendance_path, engine='openpyxl')
            df_template = preprocess_sundays(df_template)

            id_column = "Ticket No."
            if id_column not in df_template.columns or id_column not in df_attendance.columns:
                QMessageBox.critical(self, "Error", f"'{id_column}' column missing in one of the files.")
                return
            if date_column not in df_attendance.columns:
                QMessageBox.critical(self, "Error", f"'{date_column}' missing in attendance file.")
                return

            # Update template with new statuses
            status_map = dict(zip(df_attendance[id_column], df_attendance[date_column]))
            df_template[date_column] = df_template.apply(
                lambda row: status_map.get(row[id_column], row.get(date_column, '')), axis=1
            )
            df_template.to_excel(self.template_path, index=False, engine='openpyxl')

            # Generate absentee reports (fixed dir: data/absentee_reports/)
            generate_absent_reports(
                df_template, date_column, id_column, department=self.department,
                base_output_dir="data/absentee_reports"
            )

            QMessageBox.information(
                self, "Success", f"✅ Attendance updated for {date_column}!\n📁 {self.template_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Update Failed", f"Error during update:\n{e}")
