import os
import sys
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QMessageBox, QScrollArea,
    QDateEdit, QPushButton, QHBoxLayout, QDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import seaborn as sns


def resource_path(relative_path):
    """Support for PyInstaller one-file mode (bundle resources)."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class DashboardSelector(QDialog):
    """Dialog to select a date for viewing absentee dashboard."""
    def __init__(self, department, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Dashboard Date")
        self.department = department
        self.selected_date_str = None
        self.setWindowIcon(QIcon(resource_path("assets/APP_logo.ico")))

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select a date to view absentee dashboard:"))

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("View Dashboard")
        btn_ok.clicked.connect(self.accept_dialog)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def accept_dialog(self):
        selected_qdate = self.date_edit.date()
        self.selected_date_str = selected_qdate.toString("dd.MM.yyyy")
        self.accept()


class DashboardWindow(QWidget):
    """Main dashboard window showing absentee analysis."""
    def __init__(self, department, selected_date_str):
        super().__init__()
        self.setWindowTitle("Absentee Dashboard")
        self.department = department
        self.selected_date_str = selected_date_str
        self.setMinimumSize(1000, 700)
        self.showMaximized()

        # === SCROLL AREA SETUP ===
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        container_widget = QWidget()
        scroll_area.setWidget(container_widget)

        main_layout = QVBoxLayout(container_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll_area)
        self.setLayout(outer_layout)

        # === LOAD DATA LOCALLY ===
        try:
            self.absentee_data = {}
            for day in [3, 6, 10]:
                filename = f"data/absentees_reports/{day}_Consecutive_Absentees_{self.selected_date_str}.xlsx"
                if os.path.exists(filename):
                    self.absentee_data[day] = pd.read_excel(filename)
                else:
                    self.absentee_data[day] = pd.DataFrame()

            month_year = datetime.strptime(self.selected_date_str, "%d.%m.%Y").strftime("%B_%Y")
            monthly_filename = f"data/attendance_templates/Custom_Attendance_Template_{month_year}.xlsx"
            if os.path.exists(monthly_filename):
                self.monthly_data = pd.read_excel(monthly_filename, dtype=str)
            else:
                self.monthly_data = pd.DataFrame()

            self.plot_comprehensive_charts(main_layout)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dashboard data:\n{e}")

    def plot_comprehensive_charts(self, layout):
        title = QLabel(f"<h2 style='margin-bottom:20px;'>Comprehensive Absentee Dashboard for {self.selected_date_str}</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        plt.style.use('default')
        sns.set_palette("husl")

        fig, axes = plt.subplots(2, 2, figsize=(16, 9), constrained_layout=True)
        fig.suptitle(f'Department-wise Absentee Analysis - {self.selected_date_str[-4:]}',
                     fontsize=18, fontweight='bold')

        ax1, ax2, ax3, ax4 = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

        dept_absentees = {}
        date_columns = []

        if not self.monthly_data.empty:
            self.monthly_data.fillna('', inplace=True)

            # Extract valid date columns
            for col in self.monthly_data.columns:
                if col not in ['Ticket. No.', 'Name', 'Dept']:
                    try:
                        datetime.strptime(col.strip(), "%d.%m.%Y")
                        date_columns.append(col.strip())
                    except:
                        continue

            date_columns.sort(key=lambda d: datetime.strptime(d, "%d.%m.%Y"))
            self.monthly_data['Dept'] = self.monthly_data['Dept'].astype(str)

            # Aggregate absentees per department
            for dept in self.monthly_data['Dept'].unique():
                dept_df = self.monthly_data[self.monthly_data['Dept'] == dept]
                counts = []
                for date in date_columns:
                    col_data = dept_df[date] if date in dept_df.columns else []
                    abs_count = (col_data == 'A').sum()
                    counts.append(abs_count)
                dept_absentees[dept] = counts

            dates = [datetime.strptime(d, "%d.%m.%Y") for d in date_columns]

            # === Chart 1: Line Plot ===
            for dept, absentees in dept_absentees.items():
                ax1.plot(dates, absentees, marker='o', linewidth=2, label=dept, markersize=5)
            ax1.set_title('Daily Absentee Trends by Department', fontweight='bold')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Number of Absentees')
            ax1.legend(fontsize='small')
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)

            # === Chart 2: Bar Chart ===
            dept_names = list(dept_absentees.keys())
            total_absentees = [sum(v) for v in dept_absentees.values()]
            bars = ax2.bar(dept_names, total_absentees, color=['#FF6B6B', "#000000", "#AB0D0D", '#96CEB4'])
            ax2.set_title('Total Monthly Absentees by Department', fontweight='bold')
            ax2.set_xlabel('Department')
            ax2.set_ylabel('Total Absentees')
            for bar, val in zip(bars, total_absentees):
                ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2, str(val),
                         ha='center', va='bottom', fontweight='bold', fontsize=10)

            # === Chart 3: Heatmap ===
            heatmap_data = [v for v in dept_absentees.values()]
            heatmap_df = pd.DataFrame(
                heatmap_data,
                index=list(dept_absentees.keys()),
                columns=[d.strftime('%d') for d in dates]
            )
            sns.heatmap(heatmap_df, annot=True, fmt='d', cmap='Reds', ax=ax3,
                        cbar_kws={'label': 'Absentees'})
            ax3.set_title('Daily Absentee Heatmap', fontweight='bold')
            ax3.set_xlabel('Day of Month')
            ax3.set_ylabel('Department')

            # === Chart 4: Cumulative Area Plot ===
            bottom = np.zeros(len(dates))
            for dept, counts in dept_absentees.items():
                cum_values = np.cumsum(counts)
                ax4.fill_between(dates, bottom, bottom + cum_values, label=dept, alpha=0.6)
                bottom += cum_values
            ax4.set_title('Cumulative Absentees Over Time', fontweight='bold')
            ax4.set_xlabel('Date')
            ax4.set_ylabel('Cumulative Absentees')
            ax4.legend(fontsize='small')
            ax4.tick_params(axis='x', rotation=45)
        else:
            for ax in axes.flat:
                ax.axis('off')
            ax1.text(0.5, 0.5, "No data available to display charts.",
                     ha='center', va='center', fontsize=14)

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout.addWidget(canvas)
