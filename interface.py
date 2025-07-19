import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QDateEdit, QMessageBox, QListWidget, QAbstractItemView, QInputDialog
)
from PyQt5.QtCore import QDate, QThread, pyqtSignal, Qt

SETTINGS_FILE = 'settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GitHub Generator')
        self.settings = load_settings()
        self.init_ui()
        self.set_window_size(1300, 700)  # Lebar dan tinggi default lebih besar
        self.load_data()

    def init_ui(self):
        from PyQt5.QtWidgets import QTextEdit, QSplitter, QWidget
        self.splitter = QSplitter()

        # Panel kiri: dua kolom (form utama & list)
        form_widget = QWidget()
        form_hbox = QHBoxLayout(form_widget)
        form_hbox.setContentsMargins(16, 16, 16, 16)
        form_hbox.setSpacing(8)

        # Kolom kiri: field utama
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        self.username_edit = QLineEdit()
        left_col.addWidget(QLabel('Username'))
        left_col.addWidget(self.username_edit)

        self.email_edit = QLineEdit()
        left_col.addWidget(QLabel('Email'))
        left_col.addWidget(self.email_edit)

        self.github_email_edit = QLineEdit()
        left_col.addWidget(QLabel('GitHub Email'))
        left_col.addWidget(self.github_email_edit)

        self.push_per_day_edit = QLineEdit()
        self.push_per_day_edit.setPlaceholderText('e.g. 3')
        left_col.addWidget(QLabel('Push per Day'))
        left_col.addWidget(self.push_per_day_edit)

        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.folder_btn = QPushButton('Choose Project Folder')
        self.folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.folder_btn)
        left_col.addWidget(QLabel('Project Folder'))
        left_col.addLayout(folder_layout)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        left_col.addWidget(QLabel('Start Date'))
        left_col.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        left_col.addWidget(QLabel('End Date'))
        left_col.addWidget(self.end_date_edit)

        # Save & Run Buttons (side by side)
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton('Save')
        self.save_btn.clicked.connect(self.save_data)
        self.save_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        ''')
        btn_row.addWidget(self.save_btn)

        self.run_btn = QPushButton('Run')
        self.run_btn.clicked.connect(self.run_action)
        self.run_btn.setStyleSheet('''
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        ''')
        btn_row.addWidget(self.run_btn)
        left_col.addLayout(btn_row)
        left_col.addStretch()

        # Kolom kiri: list branch, commit, ext, excl (dengan margin kanan)
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        # Tambahkan margin kanan agar ada jarak dengan kolom field utama
        right_col_widget = QWidget()
        right_col_widget.setLayout(right_col)
        right_col_widget.setContentsMargins(0, 0, 16, 0)  # margin-right 24px

        # Branch Names
        branch_label_row = QHBoxLayout()
        branch_label_row.addWidget(QLabel('Branch Names'))
        self.add_branch_btn = QPushButton('+')
        self.add_branch_btn.setFixedWidth(28)
        self.add_branch_btn.clicked.connect(self.add_branch_popup)
        branch_label_row.addWidget(self.add_branch_btn)
        self.remove_branch_btn = QPushButton('-')
        self.remove_branch_btn.setFixedWidth(28)
        self.remove_branch_btn.clicked.connect(self.remove_branch_selected)
        branch_label_row.addWidget(self.remove_branch_btn)
        branch_label_row.addStretch()
        right_col.addLayout(branch_label_row)
        self.branch_list = QListWidget()
        self.branch_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.branch_list.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.branch_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.branch_list.setAlternatingRowColors(True)
        right_col.addWidget(self.branch_list)

        # Commit Messages
        commit_label_row = QHBoxLayout()
        commit_label_row.addWidget(QLabel('Commit Messages'))
        self.add_commit_btn = QPushButton('+')
        self.add_commit_btn.setFixedWidth(28)
        self.add_commit_btn.clicked.connect(self.add_commit_popup)
        commit_label_row.addWidget(self.add_commit_btn)
        self.remove_commit_btn = QPushButton('-')
        self.remove_commit_btn.setFixedWidth(28)
        self.remove_commit_btn.clicked.connect(self.remove_commit_selected)
        commit_label_row.addWidget(self.remove_commit_btn)
        commit_label_row.addStretch()
        right_col.addLayout(commit_label_row)
        self.commit_list = QListWidget()
        self.commit_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.commit_list.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.commit_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.commit_list.setAlternatingRowColors(True)
        right_col.addWidget(self.commit_list)

        # Allowed Extensions
        ext_label_row = QHBoxLayout()
        ext_label_row.addWidget(QLabel('Allowed Extensions'))
        self.add_ext_btn = QPushButton('+')
        self.add_ext_btn.setFixedWidth(28)
        self.add_ext_btn.clicked.connect(self.add_ext_popup)
        ext_label_row.addWidget(self.add_ext_btn)
        self.remove_ext_btn = QPushButton('-')
        self.remove_ext_btn.setFixedWidth(28)
        self.remove_ext_btn.clicked.connect(self.remove_ext_selected)
        ext_label_row.addWidget(self.remove_ext_btn)
        ext_label_row.addStretch()
        right_col.addLayout(ext_label_row)
        self.ext_list = QListWidget()
        self.ext_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ext_list.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.ext_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.ext_list.setAlternatingRowColors(True)
        right_col.addWidget(self.ext_list)

        # Excluded Folders
        excl_label_row = QHBoxLayout()
        excl_label_row.addWidget(QLabel('Excluded Folders'))
        self.add_excl_btn = QPushButton('+')
        self.add_excl_btn.setFixedWidth(28)
        self.add_excl_btn.clicked.connect(self.add_excl_popup)
        excl_label_row.addWidget(self.add_excl_btn)
        self.remove_excl_btn = QPushButton('-')
        self.remove_excl_btn.setFixedWidth(28)
        self.remove_excl_btn.clicked.connect(self.remove_excl_selected)
        excl_label_row.addWidget(self.remove_excl_btn)
        excl_label_row.addStretch()
        right_col.addLayout(excl_label_row)
        self.excl_list = QListWidget()
        self.excl_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.excl_list.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.excl_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.excl_list.setAlternatingRowColors(True)
        right_col.addWidget(self.excl_list)
        right_col.addStretch()

        form_hbox.addWidget(right_col_widget, 3)
        form_hbox.addLayout(left_col, 2)

        # Kanan: Log
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_label = QLabel('Log')
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_text)

        self.splitter.addWidget(form_widget)
        self.splitter.addWidget(log_widget)
        self.set_splitter_sizes(700, 500)  # default size, lebih lebar kiri

        # Footer
        footer_label = QLabel('Credits By @masdevan - GitHub')
        footer_label.setStyleSheet('color: #888; font-size: 12px; margin-top: 8px;')
        footer_label.setAlignment(Qt.AlignCenter)

        # Main layout with footer
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.splitter)
        main_layout.addWidget(footer_label)
        self.setLayout(main_layout)

    def run_action(self):
        from main import auto_commit_and_push
        self.add_log('Menjalankan auto commit & push...')
        self.run_btn.setEnabled(False)
        self.run_btn.setText('Running...')
        self.save_btn.setEnabled(False)
        # Jalankan di thread terpisah
        class Worker(QThread):
            log_signal = pyqtSignal(str)
            finished_signal = pyqtSignal()
            def run(self_):
                auto_commit_and_push(self_.log_signal.emit)
                self_.finished_signal.emit()
        self.worker = Worker()
        self.worker.log_signal.connect(self.add_log)
        self.worker.finished_signal.connect(self.on_run_finished)
        self.worker.start()

    def on_run_finished(self):
        self.run_btn.setEnabled(True)
        self.run_btn.setText('Run')
        self.save_btn.setEnabled(True)

    def set_splitter_sizes(self, left_width, right_width):
        """
        Set the width of the left (form) and right (log) panels in pixels.
        Example: self.set_splitter_sizes(400, 600)
        """
        self.splitter.setSizes([left_width, right_width])

    def set_window_size(self, width, height):
        """
        Set the main window size in pixels.
        Example: self.set_window_size(1000, 600)
        """
        self.resize(width, height)

    def add_log(self, message):
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Colorize based on message content
        color = '#333'
        lower_msg = message.lower()
        if any(w in lower_msg for w in ['berhasil', 'success', 'done', 'completed']):
            color = '#388E3C'  # green
        elif any(w in lower_msg for w in ['gagal', 'error', 'fail', 'failed']):
            color = '#D32F2F'  # red
        elif any(w in lower_msg for w in ['warning', 'peringatan']):
            color = '#FFA000'  # orange
        elif any(w in lower_msg for w in ['info', 'menjalankan', 'running']):
            color = '#1976D2'  # blue
        html = f'<span style="color:#888;">[{now}]</span> <span style="color:{color};">{message}</span>'
        self.log_text.append(html)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Pilih Folder Project')
        if folder:
            self.folder_edit.setText(folder)
            self.add_log(f'Folder project dipilih: {folder}')

    def load_data(self):
        s = self.settings
        self.username_edit.setText(s.get('username', ''))
        self.email_edit.setText(s.get('email', ''))
        self.github_email_edit.setText(s.get('github_email', ''))
        self.folder_edit.setText(s.get('project_folder', ''))
        self.push_per_day_edit.setText(str(s.get('push_per_day', '')))
        # Load branch names
        self.branch_list.clear()
        for branch in s.get('branch_names', []):
            self.branch_list.addItem(branch)
        # Load commit messages
        self.commit_list.clear()
        for msg in s.get('commit_messages', []):
            self.commit_list.addItem(msg)
        # Load allowed extensions
        self.ext_list.clear()
        for ext in s.get('allowed_extensions', []):
            self.ext_list.addItem(ext)
        # Load excluded folders
        self.excl_list.clear()
        for excl in s.get('excluded_folders', []):
            self.excl_list.addItem(excl)
        if s.get('start_date'):
            self.start_date_edit.setDate(QDate.fromString(s['start_date'], 'yyyy-MM-dd'))
        else:
            self.start_date_edit.setDate(QDate.currentDate())
        if s.get('end_date'):
            self.end_date_edit.setDate(QDate.fromString(s['end_date'], 'yyyy-MM-dd'))
        else:
            self.end_date_edit.setDate(QDate.currentDate())

    def save_data(self):
        data = {
            'username': self.username_edit.text(),
            'email': self.email_edit.text(),
            'github_email': self.github_email_edit.text(),
            'project_folder': self.folder_edit.text(),
            'push_per_day': self.push_per_day_edit.text(),
            'branch_names': [self.branch_list.item(i).text() for i in range(self.branch_list.count())],
            'commit_messages': [self.commit_list.item(i).text() for i in range(self.commit_list.count())],
            'allowed_extensions': [self.ext_list.item(i).text() for i in range(self.ext_list.count())],
            'excluded_folders': [self.excl_list.item(i).text() for i in range(self.excl_list.count())],
            'start_date': self.start_date_edit.date().toString('yyyy-MM-dd'),
            'end_date': self.end_date_edit.date().toString('yyyy-MM-dd'),
        }
        save_settings(data)
        self.add_log('Data saved successfully!')
        QMessageBox.information(self, 'Info', 'Data saved successfully!')

    def add_branch_popup(self):
        dlg = QInputDialog(self)
        dlg.setWindowTitle('Add Branch')
        dlg.setLabelText('Branch name:')
        dlg.resize(500, 120)
        # Perbesar QLineEdit di dalam QInputDialog
        line_edit = dlg.findChild(QLineEdit)
        if line_edit:
            line_edit.setMinimumWidth(500)
        ok = dlg.exec_()
        text = dlg.textValue()
        if ok and text:
            self.branch_list.addItem(text)

    def remove_branch_selected(self):
        for item in self.branch_list.selectedItems():
            self.branch_list.takeItem(self.branch_list.row(item))

    def add_commit_popup(self):
        dlg = QInputDialog(self)
        dlg.setWindowTitle('Add Commit Message')
        dlg.setLabelText('Commit message:')
        dlg.resize(500, 120)
        # Perbesar QLineEdit di dalam QInputDialog
        line_edit = dlg.findChild(QLineEdit)
        if line_edit:
            line_edit.setMinimumWidth(500)
        ok = dlg.exec_()
        text = dlg.textValue()
        if ok and text:
            self.commit_list.addItem(text)

    def remove_commit_selected(self):
        for item in self.commit_list.selectedItems():
            self.commit_list.takeItem(self.commit_list.row(item))

    def add_ext_popup(self):
        dlg = QInputDialog(self)
        dlg.setWindowTitle('Add Allowed Extension')
        dlg.setLabelText('Extension (e.g. .py):')
        dlg.resize(400, 120)
        line_edit = dlg.findChild(QLineEdit)
        if line_edit:
            line_edit.setMinimumWidth(200)
        ok = dlg.exec_()
        text = dlg.textValue()
        if ok and text:
            self.ext_list.addItem(text)

    def remove_ext_selected(self):
        for item in self.ext_list.selectedItems():
            self.ext_list.takeItem(self.ext_list.row(item))

    def add_excl_popup(self):
        dlg = QInputDialog(self)
        dlg.setWindowTitle('Add Excluded Folder')
        dlg.setLabelText('Folder name:')
        dlg.resize(400, 120)
        line_edit = dlg.findChild(QLineEdit)
        if line_edit:
            line_edit.setMinimumWidth(200)
        ok = dlg.exec_()
        text = dlg.textValue()
        if ok and text:
            self.excl_list.addItem(text)

    def remove_excl_selected(self):
        for item in self.excl_list.selectedItems():
            self.excl_list.takeItem(self.excl_list.row(item))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec_())
