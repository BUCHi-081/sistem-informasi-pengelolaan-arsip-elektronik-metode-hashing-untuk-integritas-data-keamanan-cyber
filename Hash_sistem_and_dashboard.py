from collections import deque
import sys
import hashlib
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QLabel,
    QLineEdit,
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QMenu
)

from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


# =========================================================
# DATA STORAGE
# =========================================================

arsip_data = []
pending = deque()


# =========================================================
# HASH SHA256
# =========================================================

def generate_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while chunk := file.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()


# =========================================================
# SUBMIT PENDING
# =========================================================

def submit_pending(file_path, category, uploader):

    file_name = os.path.basename(file_path)

    file_hash = generate_hash(file_path)

    # cek duplicate hash
    for item in arsip_data:

        if item["file_hash"] == file_hash:

            return False

    data = {
        "file_name": file_name,
        "file_path": file_path,
        "file_hash": file_hash,
        "category": category,
        "uploader": uploader,
        "submit_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "status": "Pending"
    }
    

    pending.append(data)

    return True


# =========================================================
# GET PENDING
# =========================================================

def get_pending(filter_by="all"):
    items = list(enumerate(pending))
    if filter_by in ["Sangat Penting", "Penting", "Kurang Penting"]:
        return [(i, item) for i, item in items if item["category"] == filter_by]
    
    return items


# =========================================================
# APPROVE PENDING
# =========================================================

def accept_pending(index):

    if index >= len(pending):

        return

    data = pending[index]

    arsip_data.append({
        "file_name": data["file_name"],
        "upload_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "uploader": data["uploader"],
        "file_hash": data["file_hash"],
        "category": data["category"],
        "status": "Approved"
    })

    del pending[index]


# =========================================================
# REJECT PENDING
# =========================================================

def reject_pending(index):

    if index >= len(pending):

        return
    
    data = pending[index]
    

    arsip_data.append({
        "file_name": data["file_name"],
        "upload_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "uploader": data["uploader"],
        "file_hash": "Rejected",
        "category": data["category"],
        "status": "Rejected"
    })

    
    del pending[index]


# FILTERING
# =========================================================

def get_arsip(filter_by="all"):

    if filter_by in ["Sangat Penting", "Penting", "Kurang Penting"]:
        
        return [
            item for item in reversed(arsip_data) 
            if item["category"] == filter_by
        ]

    return list(reversed(arsip_data))


# =========================================================
# DASHBOARD
# =========================================================

class Dashboard(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Dashboard Arsip SHA256")

        self.resize(1100, 650)

        self.setStyleSheet("""
            background-color: white;
            color: black;
        """)

        self.selected_file = None
        self.selected_category = None

        self._init_ui()

        self.switch_page("daftar")

    # =====================================================
    # INIT UI 
    # =====================================================

    def _init_ui(self):

        main_layout = QHBoxLayout(self)

        # =================================================
        # NAVIGASI
        # =================================================

        navigasi = QVBoxLayout()

        self.btn_daftar = self._make_navigasi_button(
            "Daftar Arsip",
            "daftar"
        )

        self.btn_upload = self._make_navigasi_button(
            "Upload Dokumen",
            "upload"
        )

        self.btn_konfirmasi = self._make_navigasi_button(
            "Konfirmasi",
            "konfirmasi"
        )

        navigasi.addWidget(self.btn_daftar)
        navigasi.addWidget(self.btn_upload)
        navigasi.addWidget(self.btn_konfirmasi)

        navigasi.addStretch()

        # =================================================
        # CONTENT
        # =================================================

        self.content_layout = QVBoxLayout()

        main_layout.addLayout(navigasi, 1)
        main_layout.addLayout(self.content_layout, 4)

    # =====================================================
    # NAVIGASI BUTTON
    # =====================================================

    def _make_navigasi_button(self, text, page):

        button = QPushButton(text)

        button.setFixedHeight(45)

        button.clicked.connect(
            lambda: self.switch_page(page)
        )

        return button

    # =====================================================
    # RESET STYLE
    # =====================================================

    def reset_button_styles(self):

        base_style = """
            color: black;
            background-color: #f0f0f0;
            padding: 8px;
            text-align: left;
            border-radius: 8px;
            font-size: 14px;
        """

        self.btn_daftar.setStyleSheet(base_style)
        self.btn_upload.setStyleSheet(base_style)
        self.btn_konfirmasi.setStyleSheet(base_style)

    # =====================================================
    # CLEAR CONTENT
    # =====================================================

    def clear_content(self):

        while self.content_layout.count():

            item = self.content_layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

    # =====================================================
    # CREATE TABLE
    # =====================================================

    def create_table(self, headers, widths):

        table = QTableWidget(0, len(headers))

        table.setHorizontalHeaderLabels(headers)

        table.setStyleSheet("""
            QTableWidget {
                background-color: black;
                color: white;
                gridline-color: #444;
                border: 1px solid #333;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #111;
                color: white;
                padding: 6px;
                border: 1px solid #333;
                font-weight: bold;
            }

            QTableWidget::item:selected {
                background-color: #2d89ef;
                color: white;
            }
        """)

        table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        header = table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.Interactive
        )

        for i, width in enumerate(widths):

            table.setColumnWidth(i, width)

        return table

    # =====================================================
    # SWITCH PAGE
    # =====================================================

    def switch_page(self, page):

        self.reset_button_styles()

        active_style = """
            color: blue;
            background-color: #e0e0ff;
            padding: 8px;
            text-align: left;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
        """

        self.clear_content()

        if page == "daftar":

            self.btn_daftar.setStyleSheet(active_style)

            self._build_archive_page()

        elif page == "upload":

            self.btn_upload.setStyleSheet(active_style)

            self._build_upload_page()

        elif page == "konfirmasi":

            self.btn_konfirmasi.setStyleSheet(active_style)

            self._build_confirm_page()

    # =====================================================
    # DAFTAR ARSIP
    # =====================================================

    def _build_archive_page(self):

        label = QLabel("📂 Daftar Arsip")

        label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)

        self.content_layout.addWidget(label)

        # AREA SORTING
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Filter Kategori:"))

        # Tombol Sorting
        self.current_sort = "all"
        
        options = [
            ("Semua", "all"),
            ("Sangat Penting", "Sangat Penting"),
            ("Penting", "Penting"),
            ("Kurang Penting", "Kurang Penting")
        ]

        for text, mode in options:
            btn = QPushButton(text)
            btn.setFixedWidth(120)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 4px;
                    color: black;
                    font-weight: 500;
                }
                QPushButton:hover { background-color: #e0e0ff; }
            """)
            btn.clicked.connect(lambda _, m=mode: self._change_sort(m))
            top_bar.addWidget(btn)

        top_bar.addStretch()
        self.content_layout.addLayout(top_bar)

        table = self.create_table(
            [
                "Nama Dokumen",
                "Date",
                "Uploader",
                "Hash SHA256",
                "Kategori"
            ],
            [260, 170, 150, 420, 150]
        )

        self.content_layout.addWidget(table)
        self.archive_table = table
        self._refresh_archive()

    def _change_sort(self, mode):
        self.current_sort = mode
        self._refresh_archive()

    def _refresh_archive(self):
        self.archive_table.setRowCount(0)
        
        for entry in get_arsip(self.current_sort):

            row = self.archive_table.rowCount()
            self.archive_table.insertRow(row)

            is_rejected = entry.get("status") == "Rejected"

            values = [
                entry["file_name"],
                entry["upload_time"],
                entry["uploader"],
                entry["file_hash"],
                entry["category"]
            ]

            for col, text in enumerate(values):
                item = QTableWidgetItem(text)
                item.setFlags(
                    item.flags() & ~Qt.ItemIsEditable
                )

                if is_rejected:
                    item.setForeground(QColor("red"))

                self.archive_table.setItem(row, col, item)

            self._style_category_cell(
                self.archive_table.item(row, 4),
                entry["category"],
                is_rejected
            )

    def _build_upload_page(self):

        label = QLabel("⬆️ Upload Arsip Dokumen")

        label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)

        self.content_layout.addWidget(label)

        # USER

        user_label = QLabel("User :")

        user_label.setStyleSheet("""
            font-weight: 600;
            color: #222;
        """)

        self.user_input = QLineEdit()

        self.user_input.setFixedHeight(36)

        self.user_input.setStyleSheet("""
            background-color: #e9e9e9;
            border-radius: 8px;
            padding-left: 12px;
            color: black;
        """)

        self.content_layout.addWidget(user_label)
        self.content_layout.addWidget(self.user_input)

        # FILE

        folder_label = QLabel("Masukan File :")

        folder_label.setStyleSheet("""
            font-weight: 600;
            color: #222;
            margin-top: 8px;
        """)

        self.upload_area = QPushButton("⬆")

        self.upload_area.setCursor(Qt.PointingHandCursor)

        self.upload_area.setFixedHeight(56)

        self.upload_area.setStyleSheet("""
            background-color: #e9e9e9;
            border-radius: 8px;
            font-size: 20px;
            color: #666;
        """)

        self.upload_area.clicked.connect(
            self._choose_file
        )

        self.content_layout.addWidget(folder_label)
        self.content_layout.addWidget(self.upload_area)

        # CATEGORY

        cat_label = QLabel("Kategori Dokumen :")

        cat_label.setStyleSheet("""
            font-weight: 600;
            color: #222;
            margin-top: 12px;
        """)

        self.content_layout.addWidget(cat_label)

        self.btn_kurang = self._make_category_button(
            "KURANG PENTING",
            "Kurang Penting"
        )

        self.btn_penting = self._make_category_button(
            "PENTING",
            "Penting"
        )

        self.btn_sangat = self._make_category_button(
            "SANGAT PENTING",
            "Sangat Penting"
        )

        cat_col = QVBoxLayout()

        cat_col.setSpacing(10)

        cat_col.addWidget(self.btn_kurang)
        cat_col.addWidget(self.btn_penting)
        cat_col.addWidget(self.btn_sangat)

        self.content_layout.addLayout(cat_col)

        # BUTTON

        btn_row = QHBoxLayout()

        btn_row.addStretch()

        confirm_btn = QPushButton("KONFIRMASI")

        confirm_btn.setFixedSize(180, 36)

        confirm_btn.setStyleSheet("""
            background-color: #7fdbff;
            color: white;
            border-radius: 18px;
            font-weight: 700;
        """)

        confirm_btn.clicked.connect(
            self._save_upload
        )

        btn_row.addWidget(confirm_btn)

        self.content_layout.addLayout(btn_row)

    # =====================================================
    # CATEGORY BUTTON
    # =====================================================

    def _make_category_button(self, text, category):

        button = QPushButton(text)

        button.setFixedHeight(36)

        button.setStyleSheet(
            self._category_style(category)
        )

        button.clicked.connect(
            lambda: self._select_category(category)
        )

        return button

    # =====================================================
    # CATEGORY STYLE
    # =====================================================

    def _category_style(self, category, selected=False):

        base_colors = {
            "Kurang Penting": "#cfcfcf",
            "Penting": "#f7ff99",
            "Sangat Penting": "#ffb6b6",
        }

        selected_colors = {
            "Kurang Penting": "#bfbfbf",
            "Penting": "#eafe6b",
            "Sangat Penting": "#ff9aa0",
        }

        color = (
            selected_colors[category]
            if selected
            else base_colors[category]
        )

        return f"""
            background-color: {color};
            color: black;
            border-radius: 6px;
            font-weight: 700;
        """

    # =====================================================
    # SELECT CATEGORY
    # =====================================================

    def _select_category(self, category):

        self.selected_category = category

        self.btn_kurang.setStyleSheet(
            self._category_style("Kurang Penting")
        )

        self.btn_penting.setStyleSheet(
            self._category_style("Penting")
        )

        self.btn_sangat.setStyleSheet(
            self._category_style("Sangat Penting")
        )

        if category == "Kurang Penting":

            self.btn_kurang.setStyleSheet(
                self._category_style(
                    "Kurang Penting",
                    selected=True
                )
            )

        elif category == "Penting":

            self.btn_penting.setStyleSheet(
                self._category_style(
                    "Penting",
                    selected=True
                )
            )

        elif category == "Sangat Penting":

            self.btn_sangat.setStyleSheet(
                self._category_style(
                    "Sangat Penting",
                    selected=True
                )
            )

    # =====================================================
    # CHOOSE FILE
    # =====================================================

    def _choose_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File"
        )

        if not file_path:

            return

        self.selected_file = file_path

        file_name = os.path.basename(file_path)

        self.upload_area.setText(
            f"⬆  {file_name}"
        )

        self.upload_area.setStyleSheet("""
            background-color: #e9e9e9;
            border-radius: 8px;
            font-size: 20px;
            color: black;
        """)

    # =====================================================
    # SAVE UPLOAD
    # =====================================================

    def _save_upload(self):

        if not self.selected_file or not self.selected_category:

            QMessageBox.warning(
                self,
                "Warning",
                "File atau kategori belum dipilih!"
            )

            return

        uploader = self.user_input.text() or "anonymous"

        success = submit_pending(
            self.selected_file,
            self.selected_category,
            uploader
        )

        if not success:

            QMessageBox.warning(
                self,
                "Duplicate",
                "Hash file sudah ada!"
            )

            return

        QMessageBox.information(
            self,
            "Berhasil",
            "Dokumen berhasil masuk queue!"
        )

        self.switch_page("konfirmasi")

    # =====================================================
    # HALAMAN KONFIRMASI
    # =====================================================

    def _build_confirm_page(self):

        label = QLabel("🔔 Halaman Konfirmasi")

        label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)

        self.content_layout.addWidget(label)

        # AREA FILTER
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Filter Kategori:"))

        # Tombol Filter
        self.current_confirm_filter = "all"
        
        options = [
            ("Semua", "all"),
            ("Sangat Penting", "Sangat Penting"),
            ("Penting", "Penting"),
            ("Kurang Penting", "Kurang Penting")
        ]

        for text, mode in options:
            btn = QPushButton(text)
            btn.setFixedWidth(120)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 4px;
                    color: black;
                    font-weight: 500;
                }
                QPushButton:hover { background-color: #e0e0ff; }
            """)
            btn.clicked.connect(
                lambda _, m=mode: self._change_filter_pending(m)
            )
            top_bar.addWidget(btn)

        top_bar.addStretch()
        self.content_layout.addLayout(top_bar)

        self.confirm_table = self.create_table(
            [
                "Nama Dokumen",
                "Waktu Submit",
                "Uploader",
                "Kategori",
                "Status"
            ],
            [260, 170, 150, 150, 120]
        )

        self.content_layout.addWidget(
            self.confirm_table
        )

        # KLIK KANAN
        self.confirm_table.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.confirm_table.customContextMenuRequested.connect(
            self._show_context_menu
        )

        self._refresh_confirm()

    def _change_filter_pending(self, mode):
        self.current_confirm_filter = mode
        self._refresh_confirm()

    def _refresh_confirm(self):
        self.confirm_table.setRowCount(0)
        
        for row, (original_index, entry) in enumerate(
            get_pending(self.current_confirm_filter)
        ):
            self.confirm_table.insertRow(row)

            values = [
                entry["file_name"],
                entry["submit_time"],
                entry["uploader"],
                entry["category"],
                entry["status"]
            ]

            for col, text in enumerate(values):
                item = QTableWidgetItem(text)
                item.setFlags(
                    item.flags() & ~Qt.ItemIsEditable
                )
                
                # Simpan index asli ke dalam item kolom pertama
                if col == 0:
                    item.setData(Qt.UserRole, original_index)

                self.confirm_table.setItem(
                    row,
                    col,
                    item
                )

            self._style_category_cell(
                self.confirm_table.item(row, 3),
                entry["category"]
            )

            # REJECTED = MERAH (jika status ditolak ada di queue)
            if entry["status"] == "Rejected":
                for col in range(5):
                    item = self.confirm_table.item(
                        row,
                        col
                    )

                    if item:
                        item.setForeground(
                            QColor("red")
                        )

    # =====================================================
    # CATEGORY COLOR
    # =====================================================

    def _style_category_cell(self, item, category, is_rejected=False):

        if not item:

            return

        if category == "Kurang Penting":

            item.setBackground(
                QColor("#808080")
            )

        elif category == "Penting":

            item.setBackground(
                QColor("#d4c000")
            )

        elif category == "Sangat Penting":

            item.setBackground(
                QColor("#b22222")
            )

        if is_rejected:
            item.setForeground(QColor("red"))
        else:
            item.setForeground(QColor("black"))
            

        font = item.font()

        font.setBold(True)

        item.setFont(font)

    def _show_context_menu(self, position):

        row = self.confirm_table.rowAt(
            position.y()
        )

        if row < 0:

            return
            
        # Ambil index asli yang tadi kita simpan di item kolom pertama
        item = self.confirm_table.item(row, 0)
        original_index = item.data(Qt.UserRole)

        menu = QMenu()

        approve_action = menu.addAction(
            "Approve"
        )

        reject_action = menu.addAction(
            "Reject"
        )

        action = menu.exec(
            self.confirm_table.viewport().mapToGlobal(position)
        )

        # APPROVE

        if action == approve_action:

            reply = QMessageBox.question(
                self,
                "Konfirmasi",
                "Approve dokumen ini?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:

                accept_pending(original_index)

                QMessageBox.information(
                    self,
                    "Berhasil",
                    "Dokumen berhasil diapprove"
                )

                self.switch_page("daftar")

        elif action == reject_action:

            reply = QMessageBox.question(
                self,
                "Konfirmasi",
                "Reject dokumen ini?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:

                reject_pending(original_index)

                self.switch_page("konfirmasi")

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = Dashboard()

    window.show()

    sys.exit(app.exec())