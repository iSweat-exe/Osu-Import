import os
import zipfile
import tempfile
import subprocess
import shutil
import time
import psutil
import random
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QProgressBar, QFileDialog, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QFontDatabase, QIcon
import logging
from datetime import datetime

# Créer le dossier logs s'il n'existe pas
os.makedirs("logs", exist_ok=True)

# Config du logger
logging.basicConfig(
    filename="logs/app.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

OSU_PROCESS_NAME = "osu!.exe"
IMPORTER_MEMORY_MAX = 80 * 1024 * 1024  # 80 Mo

class ImportWorker(QThread):
    progress_signal = Signal(int, int)
    imported_file_signal = Signal(str)
    status_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, path, batch_size=5):
        super().__init__()
        self.path = path
        self.batch_size = batch_size
        self.temp_dir = None
        logging.debug("ImportWorker initialized with path: %s", path)

    def run(self):
        logging.info("Import thread started.")
        try:
            if self.path.endswith('.zip'):
                logging.debug("Path is a ZIP file. Creating temporary directory...")
                self.temp_dir = tempfile.mkdtemp()
                self.status_signal.emit(f"Extracting '{self.path}' to temporary folder...")
                with zipfile.ZipFile(self.path, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_dir)
                logging.info("ZIP file extracted to: %s", self.temp_dir)
                search_path = self.temp_dir
            else:
                search_path = self.path

            if not os.path.isdir(search_path):
                error_msg = f"Directory not found at '{search_path}'"
                self.status_signal.emit(f"Error: {error_msg}")
                logging.error(error_msg)
                self.finished_signal.emit()
                return

            osz_files = [f for f in os.listdir(search_path) if f.endswith('.osz')]
            total = len(osz_files)
            success_count = 0

            logging.info("Found %d .osz file(s) to import.", total)
            self.status_signal.emit(f"Found {total} .osz file(s). Starting import...")

            for i in range(0, total, self.batch_size):
                batch = osz_files[i:i+self.batch_size]
                batch_number = i // self.batch_size + 1
                logging.debug("Processing batch %d with %d files", batch_number, len(batch))
                self.status_signal.emit(f"Launching batch {batch_number} with {len(batch)} files...")

                for osz_file in batch:
                    full_path = os.path.join(search_path, osz_file)
                    try:
                        logging.debug("Starting file: %s", full_path)
                        os.startfile(full_path)
                    except Exception as e:
                        error_msg = f"Failed to launch '{osz_file}': {e}"
                        self.status_signal.emit(error_msg)
                        logging.error(error_msg)

                wait_for_imports(len(batch))
                logging.debug("Batch %d completed.", batch_number)
                success_count += len(batch)

                imported_file = random.choice(batch)
                self.imported_file_signal.emit(imported_file)
                self.progress_signal.emit(success_count, total)

            success_msg = f"✅ Finished: {success_count}/{total} beatmaps successfully imported."
            self.status_signal.emit(success_msg)
            logging.info(success_msg)
            self.finished_signal.emit()

        except Exception as e:
            logging.exception("Unexpected error during import:")
            self.status_signal.emit(f"An error occurred: {e}")
            self.finished_signal.emit()

        finally:
            if self.temp_dir and os.path.exists(self.temp_dir):
                logging.debug("Attempting to delete temp folder: %s", self.temp_dir)
                for _ in range(5):
                    try:
                        shutil.rmtree(self.temp_dir)
                        logging.info("Temporary folder deleted: %s", self.temp_dir)
                        break
                    except PermissionError:
                        logging.warning("Temp folder locked. Retrying...")
                        time.sleep(1)
                else:
                    logging.error("Temporary folder %s could not be deleted. Please delete it manually.", self.temp_dir)

def count_import_processes():
    count = 0
    for proc in psutil.process_iter(['name', 'memory_info']):
        if proc.info['name'] == OSU_PROCESS_NAME:
            try:
                if proc.memory_info().rss < IMPORTER_MEMORY_MAX:
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logging.warning("Process access error: %s", e)
                continue
    logging.debug("Found %d osu! import processes running.", count)
    return count

def wait_for_imports(expected_count):
    logging.debug("Waiting for %d import(s) to finish...", expected_count)
    while True:
        current = count_import_processes()
        if current == 0:
            logging.debug("All imports finished.")
            break
        time.sleep(0.2)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        logging.info("Application started. Initializing main window.")
        self.setWindowTitle("osu! Beatmap Importer")
        self.resize(800, 350)

        font_id = QFontDatabase.addApplicationFont("fonts/Aller_Bd.ttf")
        if font_id == -1:
            logging.warning("Failed to load font: Aller_Bd.ttf. Using fallback font.")
            font_family = "Segoe UI"
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            logging.info("Custom font loaded: %s", font_family)

        self.setStyleSheet(f"""
QWidget {{
    background-color: #121212;
    color: #e8a2ff;
    font-family: '{font_family}', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 16px;
}}

QPushButton {{
    background-color: #e85dff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    color: white;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: #f0a3ff;
}}

QPushButton:pressed {{
    background-color: #c048c4;
}}

QProgressBar {{
    border: 2px solid #e85dff;
    border-radius: 10px;
    background-color: #2a2a2a;
    height: 20px;
    text-align: center;
    color: white;
    font-weight: bold;
}}

QProgressBar::chunk {{
    border-radius: 8px;
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #ff6fff, stop: 1 #cc00cc
    );
}}
""")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Osu!Import")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #e85dff;")
        self.layout.addWidget(self.title_label)

        self.info_label = QLabel("Select a .zip file or directory containing .osz files.")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.imported_label = QLabel("")
        self.imported_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.imported_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)

        self.select_zip_btn = QPushButton("Select .zip file")
        self.select_zip_btn.clicked.connect(self.select_zip)
        button_layout.addWidget(self.select_zip_btn)

        self.select_dir_btn = QPushButton("Select directory")
        self.select_dir_btn.clicked.connect(self.select_dir)
        button_layout.addWidget(self.select_dir_btn)

        self.import_btn = QPushButton("Start Import")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.on_import_btn_clicked)
        self.layout.addWidget(self.import_btn)

        self.footer_label = QLabel()
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setTextFormat(Qt.RichText)
        self.footer_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.footer_label.setOpenExternalLinks(False)
        self.footer_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.footer_label.setText(
            'Developed by <a href="https://osu.ppy.sh/users/35767175" style="color:#f0a3ff; text-decoration:underline;">iSweat</a>'
        )
        self.footer_label.linkActivated.connect(self.open_link)
        self.layout.addWidget(self.footer_label)

        self.worker = None
        self.path = None
        self.importing = False

    def open_link(self, url):
        logging.info("Opening external URL: %s", url)
        QDesktopServices.openUrl(QUrl(url))

    def select_zip(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select ZIP file", "", "Zip files (*.zip)")
        if file_path:
            logging.info("ZIP file selected: %s", file_path)
            self.path = file_path
            self.info_label.setText(f"Selected ZIP: {os.path.basename(file_path)}")
            self.import_btn.setEnabled(True)
            self.imported_label.setText("")
            self.progress_bar.setValue(0)

    def select_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory with .osz files")
        if dir_path:
            logging.info("Directory selected: %s", dir_path)
            self.path = dir_path
            self.info_label.setText(f"Selected Directory: {dir_path}")
            self.import_btn.setEnabled(True)
            self.imported_label.setText("")
            self.progress_bar.setValue(0)

    def on_import_btn_clicked(self):
        if not self.importing:
            if self.import_btn.text() == "Ok":
                logging.debug("Reset button clicked.")
                self.reset_app()
            else:
                logging.debug("Starting import process...")
                self.start_import()

    def start_import(self):
        if not self.path:
            logging.warning("Start import clicked with no path selected.")
            QMessageBox.warning(self, "No path selected", "Please select a .zip file or directory first.")
            return

        self.importing = True
        self.import_btn.setEnabled(False)
        self.select_zip_btn.setEnabled(False)
        self.select_dir_btn.setEnabled(False)

        self.worker = ImportWorker(self.path)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.imported_file_signal.connect(self.update_imported_file)
        self.worker.status_signal.connect(self.update_status)
        self.worker.finished_signal.connect(self.import_finished)
        self.worker.start()
        logging.info("ImportWorker thread started.")

    def import_finished(self):
        logging.info("Import process completed.")
        self.importing = False
        self.import_btn.setText("Ok")
        self.import_btn.setEnabled(True)
        self.select_zip_btn.setEnabled(True)
        self.select_dir_btn.setEnabled(True)

    def reset_app(self):
        logging.debug("Resetting UI state.")
        self.path = None
        self.import_btn.setText("Start Import")
        self.import_btn.setEnabled(False)
        self.info_label.setText("Select a .zip file or directory containing .osz files.")
        self.imported_label.setText("")
        self.progress_bar.setValue(0)

    def update_progress(self, success_count, total):
        logging.debug("Progress updated: %d/%d", success_count, total)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(success_count)

    def update_imported_file(self, file_name):
        logging.info("File imported: %s", file_name)
        self.imported_label.setText(f"Imported: '{file_name}'")

    def update_status(self, status):
        logging.info("Status updated: %s", status)
        self.info_label.setText(status)


if __name__ == '__main__':
    import sys
    logging.info("Launching application...")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
