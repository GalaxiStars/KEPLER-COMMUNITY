import os
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest

class DownloadManager(QObject):
    download_requested = Signal(QWebEngineDownloadRequest)

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(QWebEngineDownloadRequest)
    def on_download_requested(self, download: QWebEngineDownloadRequest):
        download_path, _ = QFileDialog.getSaveFileName(
            None, "Save File", download.downloadFileName()
        )
        if download_path:
            download.setPath(download_path)
            download.accept()
            download.finished.connect(lambda: self.on_download_finished(download))

    @Slot()
    def on_download_finished(self, download):
        print(f"Download finished: {download.path()}")