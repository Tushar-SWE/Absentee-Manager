import os
import sys
import pandas as pd
from datetime import datetime
import shutil

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QGroupBox, QProgressBar, QMessageBox,
    QFileDialog, QDialog, QDateEdit, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QIcon

from gui.file_manager import (
    download_template,
    upload_daily_attendance,
    upload_monthly_template
)
from gui.dashboard import DashboardWindow, DashboardSelector
from gui.dailogs import alert_success, alert_error
from gui.reports_preview import show_report_preview


# Replace entire MainWindow class with this one
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



class MainWindow(QMainWindow):
    def __init__(self, department, username, login_callback=None):
        super().__init__()
        self.department = department
        self.username = username
        self.login_callback = login_callback
        self.setWindowIcon(QIcon(resource_path("assets/APP_logo.ico")))
        self.setWindowTitle(f"Absentee Manager - {department}")
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.setCentralWidget(main_widget)

        # Sidebar
        sidebar = QWidget()
        sidebar.setStyleSheet("background-color: #234d82; border-radius: 10px;")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(20)

        self.stack = QStackedWidget()

        # Pages
        self.page_dashboard = self.create_dashboard_page()
        self.page_reports = self.create_reports_page()

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_reports)

        button_info = [
            ("🏠 Dashboard", lambda: self.stack.setCurrentWidget(self.page_dashboard)),
            ("📊 Reports & Analytics", lambda: self.stack.setCurrentWidget(self.page_reports)),
            ("🔒 Logout", self.logout),
            ("🧹 Delete History", self.cleanup_directories)
        ]

        for text, callback in button_info:
            btn = QPushButton(text)
            btn.setFont(QFont("Segoe UI", 13))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    color: white;
                    padding: 14px;
                    border-radius: 6px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3d566e;
                }
            """)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

    def create_dashboard_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: #3b69a3;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(60, 30, 60, 30)
        layout.setSpacing(35)

        # === Title with Logo on Top ===
        top_row = QHBoxLayout()
        top_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Absentee Control Framework")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        logo = QLabel()
        logo.setPixmap(QPixmap(resource_path("assets/logo.png")).scaled(480, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                                        Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignRight)
        logo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        top_row.addWidget(title)
        top_row.addWidget(logo)
        layout.addLayout(top_row)

        # === Subtitle ===
        subtitle = QLabel("Streamline attendance management with our comprehensive tracking system. "
                        "Upload and manage employee attendance records efficiently.")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # === User Info ===
        user_info = QLabel(f"🏢 Department: {self.department}    👤 User: {self.username}")
        user_info.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info.setStyleSheet("background-color: #2980b9; color: white; padding: 10px; border-radius: 15px;")
        layout.addWidget(user_info)

        # === Upload Section ===
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(40)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Daily Upload Card
        daily_card = QGroupBox()
        daily_card.setStyleSheet("QGroupBox { border: 1px solid #d0d0d0; border-radius: 12px; }")
        daily_layout = QVBoxLayout(daily_card)
        daily_layout.setContentsMargins(20, 25, 20, 20)
        daily_layout.setSpacing(10)

        daily_icon = QLabel("📅")
        daily_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        daily_icon.setFont(QFont("Segoe UI", 30))
        daily_layout.addWidget(daily_icon)

        daily_title = QLabel("Upload Daily Attendance")
        daily_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        daily_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        daily_layout.addWidget(daily_title)

        daily_desc = QLabel("Upload daily attendance records for real-time tracking and immediate processing. "
                            "Perfect for day-to-day attendance management.")
        daily_desc.setWordWrap(True)
        daily_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        daily_layout.addWidget(daily_desc)

        daily_formats = QLabel("Supported formats: CSV, Excel\nMax file size: 10MB")
        daily_formats.setFont(QFont("Segoe UI", 9))
        daily_formats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        daily_layout.addWidget(daily_formats)

        daily_btn = QPushButton("Select Daily File")
        daily_btn.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; border-radius: 6px;")
        daily_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        daily_btn.clicked.connect(self.upload_attendance)
        daily_layout.addWidget(daily_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Monthly Upload Card
        monthly_card = QGroupBox()
        monthly_card.setStyleSheet("QGroupBox { border: 1px solid #d0d0d0; border-radius: 12px; }")
        monthly_layout = QVBoxLayout(monthly_card)
        monthly_layout.setContentsMargins(20, 25, 20, 20)
        monthly_layout.setSpacing(10)

        monthly_icon = QLabel("📊")
        monthly_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        monthly_icon.setFont(QFont("Segoe UI", 30))
        monthly_layout.addWidget(monthly_icon)

        monthly_title = QLabel("Upload Monthly Attendance")
        monthly_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        monthly_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        monthly_layout.addWidget(monthly_title)

        monthly_desc = QLabel("Upload comprehensive monthly attendance reports for detailed analysis and payroll "
                            "processing. Ideal for bulk data management.")
        monthly_desc.setWordWrap(True)
        monthly_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        monthly_layout.addWidget(monthly_desc)

        monthly_formats = QLabel("Supported formats: CSV, Excel\nMax file size: 50MB")
        monthly_formats.setFont(QFont("Segoe UI", 9))
        monthly_formats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        monthly_layout.addWidget(monthly_formats)

        monthly_btn = QPushButton("Select Monthly File")
        monthly_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px; border-radius: 6px;")
        monthly_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        monthly_btn.clicked.connect(self.upload_monthly_template)
        monthly_layout.addWidget(monthly_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        cards_layout.addWidget(daily_card)
        cards_layout.addWidget(monthly_card)
        layout.addLayout(cards_layout)

        # === Feature Section ===
        features_layout = QHBoxLayout()
        features_layout.setSpacing(25)
        features_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def create_feature_card(icon, title, desc):
            box = QVBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI", 20))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Segoe UI", 9))
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            box.addWidget(icon_label)
            box.addWidget(title_label)
            box.addWidget(desc_label)

            frame = QGroupBox()
            frame.setLayout(box)
            frame.setStyleSheet("QGroupBox { border: none; }")
            return frame

        features_layout.addWidget(create_feature_card("⚙️", "Automated Processing", "Instant validation and processing of attendance data"))
        features_layout.addWidget(create_feature_card("🔒", "Secure Upload", "Enterprise-grade security for sensitive employee data"))
        features_layout.addWidget(create_feature_card("📈", "Real-time Reports", "Generate comprehensive attendance analytics instantly"))

        layout.addLayout(features_layout)

        return page


    def create_reports_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: #3b69a3;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(35)

        # === Title and Logo ===
        top_row = QHBoxLayout()
        top_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("📊 Reports & Analytics")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        logo = QLabel()
        logo.setPixmap(QPixmap(resource_path("assets/logo.png")).scaled(160, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                        Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignRight)
        logo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        top_row.addWidget(title)
        top_row.addWidget(logo)
        layout.addLayout(top_row)

        # === Subtitle ===
        subtitle = QLabel("Generate absentee reports and view analytical charts for better insights.")
        subtitle.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        subtitle.setStyleSheet("color: white;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # === Cards Layout ===
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def create_modern_card(title, description, preview_widget: QWidget, btn_text, bg_color, btn_color, on_click_callback):
            card = QGroupBox()
            card.setTitle("")
            card.setStyleSheet(f"""
                QGroupBox {{
                    background-color: {bg_color};
                    border-radius: 20px;
                    padding: 20px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(16)

            title_label = QLabel(f"<b>{title}</b>")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("font-size: 20px; color: #222;")

            desc_label = QLabel(description)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setStyleSheet("color: #444; font-size: 12px;")
            desc_label.setWordWrap(True)

            card_layout.addWidget(title_label)
            card_layout.addWidget(desc_label)
            card_layout.addWidget(preview_widget)

            btn = QPushButton(btn_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_color};
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    font-size: 13px;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: {QColor(btn_color).darker(120).name()};
                }}
            """)
            btn.clicked.connect(on_click_callback)

            card_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            return card

        # === Preview Table Widget ===
        preview_widget = QWidget()
        preview_layout = QGridLayout(preview_widget)
        preview_layout.setSpacing(10)

        headers = ["Type", "File", "Status", "Preview"]
        data = [
            ["🟢 3 Days", "3_Absentees.xlsx", "✅ Ready", "🗂 Available"],
            ["🆕 New", "New_Absentees.xlsx", "✅ Ready", "🗂 Available"]
        ]

        for col, header_text in enumerate(headers):
            header = QLabel(f"<b>{header_text}</b>")
            header.setStyleSheet("color: #222; font-size: 11px;")
            preview_layout.addWidget(header, 0, col)

        for row, row_data in enumerate(data, 1):
            for col, cell in enumerate(row_data):
                label = QLabel(cell)
                label.setStyleSheet("font-size: 11px; color: #333;")
                preview_layout.addWidget(label, row, col)

        # === Dashboard Preview Widget ===
        dashboard_widget = QWidget()
        dash_layout = QVBoxLayout(dashboard_widget)
        label = QLabel("📈 Chart Preview Placeholder")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            font-size: 14px;
            color: #333;
        """)
        dash_layout.addWidget(label)

        # === Report Card: Preview Reports ===
        preview_card = create_modern_card(
            title="📂 Preview Absentee Reports",
            description="View formatted Excel reports with data tables and summaries.",
            preview_widget=preview_widget,
            btn_text="📑 Open Report Viewer",
            bg_color="#e6f4ea",
            btn_color="#28a745",
            on_click_callback=self.preview_reports_dialog
        )

        # === Dashboard Card: Analytics Dashboard ===
        dashboard_card = create_modern_card(
            title="📊 Dashboard Overview",
            description=(
            "<span style='color:#f0f0f0;'>"
            "Explore interactive charts and trends for absenteeism and attendance.<br>"
            "Gain actionable insights with dynamic filters and export options."
            "</span>"
            ),
            preview_widget=dashboard_widget,
            btn_text="📊 View Analytics Dashboard",
            bg_color="#253a5e",
            btn_color="#1a2653",
            on_click_callback=self.open_dashboard
        )
        # Enhance dashboard_card visuals (removed box-shadow)
        dashboard_card.setStyleSheet("""
            QGroupBox {
            background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #253a5e, stop:1 #4b5e8e
            );
            border-radius: 24px;
            padding: 24px;
            }
        """)
        for child in dashboard_card.findChildren(QLabel):
            child.setStyleSheet(child.styleSheet() + "color: #f0f0f0;")

        cards_layout.addWidget(preview_card)
        cards_layout.addWidget(dashboard_card)
        layout.addLayout(cards_layout)

        # === Feature Highlights ===
        layout.addSpacing(30)
        features_layout = QHBoxLayout()
        features_layout.setSpacing(40)
        features_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        features = [
            ("⚡", "Real-time Updates", "Absentee reports update immediately after daily upload."),
            ("🛠", "Custom Views", "Focus on date-wise or department-specific analysis."),
            ("📤", "Export Ready", "Download data in Excel and graph formats for presentations."),
        ]

        for icon, title_text, desc_text in features:
            box = QVBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("font-size: 26px;")

            title_label = QLabel(f"<b>{title_text}</b>")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("font-size: 13px; color: white; margin-top: 6px;")

            desc_label = QLabel(desc_text)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setStyleSheet("font-size: 11px; color: #f0f0f0;")
            desc_label.setWordWrap(True)

            box.addWidget(icon_label)
            box.addWidget(title_label)
            box.addWidget(desc_label)

            feature_group = QGroupBox()
            feature_group.setStyleSheet("QGroupBox { border: none; }")
            feature_group.setLayout(box)
            features_layout.addWidget(feature_group)

        layout.addLayout(features_layout)
        return page


    # ====== Functional Actions ======
    def download_template(self):
        try:
            download_template(self.department)
            alert_success("Template downloaded successfully.")
        except Exception as e:
            alert_error(f"Failed to download template:\n{e}")

    def upload_attendance(self):
        try:
            upload_daily_attendance(self.department, parent=self)
            alert_success("Daily attendance uploaded successfully.")
        except Exception as e:
            alert_error(f"Upload failed:\n{e}")

    def upload_monthly_template(self):
        try:
            upload_monthly_template(self.department)
            alert_success("Monthly template uploaded successfully.")
        except Exception as e:
            alert_error(f"Monthly template upload failed:\n{e}")

    def preview_reports_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Report Date")
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout()
        label = QLabel("📅 Select a date to preview reports:")
        label.setFont(QFont("Segoe UI", 10))

        date_picker = QDateEdit()
        date_picker.setCalendarPopup(True)
        date_picker.setDate(QDate.currentDate())
        date_picker.setDisplayFormat("dd.MM.yyyy")

        preview_btn = QPushButton("🔍 Preview")
        preview_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 6px;")
        preview_btn.clicked.connect(lambda: self.preview_selected_date(date_picker.date(), dialog))

        layout.addWidget(label)
        layout.addWidget(date_picker)
        layout.addWidget(preview_btn)
        dialog.setLayout(layout)
        dialog.exec()

    def preview_selected_date(self, qdate: QDate, dialog):
        selected_date_str = qdate.toString("dd.MM.yyyy")
        dialog.accept()

        dept_folder = os.path.join("data/absentee_reports", self.department)
        report_files = [
            f"{count}_Consecutive_Absentees_{selected_date_str}.xlsx" for count in [3, 6, 10]
        ] + [f"New_Absentees_{selected_date_str}.xlsx"]

        found = any(os.path.exists(os.path.join(dept_folder, file)) for file in report_files)

        if found:
            show_report_preview(self.department, selected_date_str)
        else:
            alert_error(f"No absentee reports found for {selected_date_str}.")

    def open_dashboard(self):
        try:
            dialog = DashboardSelector(self.department)
            if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_date_str:
                self.dashboard_window = DashboardWindow(self.department, dialog.selected_date_str)
                self.dashboard_window.show()
        except Exception as e:
            alert_error(f"Failed to open dashboard:\\n{e}")

    def logout(self):
        self.close()
        if self.login_callback:
            self.login_callback()

    def cleanup_directories(self):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete all history in the 'data' folder?\n"
            "⚠️ This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            data_dir = "data"
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    file_path = os.path.join(data_dir, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.remove(file_path)
                            print(f"🧹 Deleted file: {file_path}")
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            print(f"🧹 Deleted folder: {file_path}")
                    except PermissionError:
                        print(f"❌ Permission denied: {file_path} — it might be open or locked.")
                    except Exception as e:
                        print(f"⚠️ Failed to delete {file_path}: {e}")
            QMessageBox.information(self, "Cleanup Complete", "All history has been deleted successfully.")


