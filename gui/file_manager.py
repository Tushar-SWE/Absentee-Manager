import os
import shutil
import pandas as pd
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QSpinBox, QComboBox, QHBoxLayout,
    QLabel, QPushButton, QDateEdit
)
from PyQt6.QtCore import QDate
from core.utils import get_month_name, ensure_folder, preprocess_sundays
from core.reports import generate_absent_reports

# Constants
ID_COLUMN = "Ticket. No."
DATA_TEMPLATE_DIR = "data/templates"
UPLOADS_DIR = "data/uploads"


class TemplateUploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📤 Select Month and Year for Upload")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        # Month selection
        month_layout = QHBoxLayout()
        month_label = QLabel("Month:")
        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        month_layout.addWidget(month_label)
        month_layout.addWidget(self.month_combo)

        # Year selection
        year_layout = QHBoxLayout()
        year_label = QLabel("Year:")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(QDate.currentDate().year())
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_spin)

        # Upload button
        upload_btn = QPushButton("⬆ Upload")
        upload_btn.clicked.connect(self.accept)

        # Combine layouts
        layout.addLayout(month_layout)
        layout.addLayout(year_layout)
        layout.addWidget(upload_btn)
        self.setLayout(layout)

    def get_selected_month_year(self):
        return self.month_combo.currentIndex() + 1, self.year_spin.value()


class TemplateDownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📅 Select Month and Year")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        # Month selection
        month_layout = QHBoxLayout()
        month_label = QLabel("Month:")
        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        month_layout.addWidget(month_label)
        month_layout.addWidget(self.month_combo)
        layout.addLayout(month_layout)

        # Year selection
        year_layout = QHBoxLayout()
        year_label = QLabel("Year:")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(QDate.currentDate().year())
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_spin)
        layout.addLayout(year_layout)

        # Submit button
        download_btn = QPushButton("⬇ Download Template")
        download_btn.clicked.connect(self.accept)
        layout.addWidget(download_btn)

        self.setLayout(layout)

    def get_selected_month_year(self):
        return self.month_combo.currentIndex() + 1, self.year_spin.value()


def download_template(department, parent=None):
    dialog = TemplateDownloadDialog(parent)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return

    month, year = dialog.get_selected_month_year()
    filename = f"Empty_Attendance_Template_{get_month_name(month)}_{year}.xlsx"
    local_path = os.path.join(DATA_TEMPLATE_DIR, filename)

    ensure_folder(os.path.dirname(local_path))

    if not os.path.exists(local_path):
        QMessageBox.critical(parent, "❌ Not Found", f"Template not found locally:\n{local_path}")
        return

    save_path, _ = QFileDialog.getSaveFileName(parent, "Save Template As", filename, "Excel Files (*.xlsx)")
    if save_path:
        shutil.copy(local_path, save_path)
        QMessageBox.information(parent, "✅ Downloaded", f"Template saved to:\n{save_path}")


def upload_monthly_template(department, parent=None):
    dialog = TemplateUploadDialog(parent)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return

    month, year = dialog.get_selected_month_year()
    filename = f"Custom_Attendance_Template_{get_month_name(month)}_{year}.xlsx"
    dest_path = os.path.join(DATA_TEMPLATE_DIR, department, filename)
    ensure_folder(os.path.dirname(dest_path))

    file_dialog = QFileDialog(parent)
    file_dialog.setNameFilter("Excel Files (*.xlsx *.xls)")
    if file_dialog.exec():
        file_path = file_dialog.selectedFiles()[0]
    else:
        return

    try:
        shutil.copy(file_path, dest_path)
        QMessageBox.information(parent, "✅ Upload Success", f"Saved locally as:\n{dest_path}")
    except Exception as e:
        QMessageBox.critical(parent, "❌ Upload Failed", str(e))


def upload_daily_attendance(department, parent: QWidget = None):
    dialog = QDialog(parent)
    dialog.setWindowTitle("📅 Select Attendance Date")
    dialog.setFixedSize(300, 150)

    layout = QVBoxLayout(dialog)
    label = QLabel("Choose attendance date:")
    label.setStyleSheet("font-size: 14px;")
    date_picker = QDateEdit()
    date_picker.setCalendarPopup(True)
    date_picker.setDate(QDate.currentDate())
    date_picker.setDisplayFormat("dd.MM.yyyy")

    next_btn = QPushButton("Next ➡")
    next_btn.setStyleSheet("background-color: #2563eb; color: white; padding: 6px;")

    def proceed_upload():
        selected_date = date_picker.date().toString("dd.MM.yyyy")
        dialog.accept()
        start_file_upload(department, selected_date, parent)

    next_btn.clicked.connect(proceed_upload)

    layout.addWidget(label)
    layout.addWidget(date_picker)
    layout.addWidget(next_btn)

    dialog.exec()


def start_file_upload(department, date_str, parent: QWidget = None):
    QMessageBox.information(parent, "📤 Upload Instruction",
                            f"Please upload file containing column for date: {date_str}")

    file_dialog = QFileDialog(parent)
    file_dialog.setNameFilter("Excel Files (*.xlsx *.xls)")
    if file_dialog.exec():
        file_path = file_dialog.selectedFiles()[0]
    else:
        return

    dest_folder = os.path.join(UPLOADS_DIR, department)
    ensure_folder(dest_folder)
    dest_path = os.path.join(dest_folder, f"Attendance_{date_str}.xlsx")

    try:
        shutil.copy(file_path, dest_path)
        QMessageBox.information(parent, "✅ Upload Success", f"Saved to:\n{dest_path}")
    except Exception as e:
        QMessageBox.critical(parent, "❌ Upload Error", f"Could not save file:\n{str(e)}")
        return

    # Determine the template file name
    month_year = datetime.strptime(date_str, "%d.%m.%Y").strftime("%B_%Y")
    template_name = f"Custom_Attendance_Template_{month_year}.xlsx"
    template_path = os.path.join(DATA_TEMPLATE_DIR, department, template_name)

    if not os.path.exists(template_path):
        QMessageBox.critical(parent, "❌ Error", f"Template not found locally:\n{template_name}")
        return

    try:
        df_template = pd.read_excel(template_path, engine='openpyxl')
        df_attendance = pd.read_excel(dest_path, engine='openpyxl')
        df_template = preprocess_sundays(df_template)

        if ID_COLUMN not in df_template.columns or ID_COLUMN not in df_attendance.columns:
            QMessageBox.critical(parent, "❌ Missing Column",
                                 f"Column '{ID_COLUMN}' not found in one of the files.")
            return
        if date_str not in df_attendance.columns:
            QMessageBox.critical(parent, "❌ Missing Date", f"Date '{date_str}' not found in uploaded file.")
            return

        # Fill attendance
        status_map = dict(zip(df_attendance[ID_COLUMN], df_attendance[date_str]))
        df_template[date_str] = df_template.apply(
            lambda row: status_map.get(row[ID_COLUMN], row.get(date_str, "")),
            axis=1
        )
        df_template.to_excel(template_path, index=False, engine='openpyxl')
        QMessageBox.information(parent, "✅ Attendance Updated", f"Attendance updated for {date_str}")

        # Generate reports locally
        generate_absent_reports(df_template, date_str, ID_COLUMN, department, base_output_dir="data/absentee_reports")
        QMessageBox.information(parent, "📄 Report Generated", f"Reports generated for {date_str}")

    except Exception as e:
        QMessageBox.critical(parent, "❌ Processing Error", f"Error while processing files:\n{str(e)}")
