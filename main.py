import sys
import subprocess
import re
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QProgressBar, QLabel
from PySide6.QtCore import QThread, Signal

class DownloadWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    title_found = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.title = url

    def run(self):
        try:
            title_process = subprocess.run(
                ['yt-dlp', '--get-title', '--no-warnings', self.url],
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=False
            )
            if title_process.returncode == 0 and title_process.stdout.strip():
                self.title = title_process.stdout.strip()
        except FileNotFoundError:
            # yt-dlp не найден
            self.finished.emit("Ошибка: yt-dlp не найден. Убедитесь, что он установлен и доступен в PATH.")
            return

        self.title_found.emit(self.title)

        process = subprocess.Popen(
            ['yt-dlp', self.url, '--progress'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        for line in iter(process.stdout.readline, ''):
            match = re.search(r'\[download\]\s+([0-9\.]+)%', line)
            if match:
                percentage = float(match.group(1))
                self.progress.emit(int(percentage))
            
            print(line.strip())

        process.wait()
        if process.returncode == 0:
            self.finished.emit(f"Загрузка '{self.title}' завершена!")
        else:
            self.finished.emit(f"Ошибка при загрузке '{self.title}' (код: {process.returncode})")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("yt-dlp Downloader")
        self.setMinimumSize(400, 300)

        central_widget = QWidget()
        self.layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Вставьте сюда ссылку на видео и нажмите Enter...")
        self.layout.addWidget(self.url_input)
        self.url_input.returnPressed.connect(self.start_download)

        self.workers = {}

    def start_download(self):
        url = self.url_input.text()
        if not url:
            return

        download_widget = QWidget()
        download_layout = QVBoxLayout(download_widget)
        download_layout.setContentsMargins(0, 5, 0, 5)

        title_label = QLabel("Получение информации...")
        progress_bar = QProgressBar()

        download_layout.addWidget(title_label)
        download_layout.addWidget(progress_bar)
        
        self.layout.insertWidget(1, download_widget)

        worker = DownloadWorker(url)
        
        worker.title_found.connect(title_label.setText)
        worker.progress.connect(progress_bar.setValue)
        worker.finished.connect(lambda msg, w=worker: self.on_download_finished(w, msg))
        
        self.workers[worker] = download_widget
        worker.start()

        self.url_input.clear()

    def on_download_finished(self, worker, msg):
        print(msg)
        if worker in self.workers:
            widget_to_remove = self.workers.pop(worker)
            widget_to_remove.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
