import os
from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QPainter, QPainterPath, QRegion
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from download_manager import DownloadManager
from page_templates import PageTemplates
from error_handling import ErrorHandler

download_manager = DownloadManager()

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._loading_error = False
        self._web_view = parent
        self._error_handled = False

    def javaScriptConsoleMessage(self, level, message, line, source):
        # Suppress console messages
        pass

    def certificateError(self, error):
        if not self._error_handled:
            self._error_handled = True
            self._loading_error = True
            # Stop any current load
            self._web_view.stop()
            # Show our error page
            ErrorHandler.show_error_page(self._web_view, self._web_view.url().toString())
        return True

    def loadStarted(self):
        self._loading_error = False
        self._error_handled = False

    def loadFinished(self, ok):
        if not ok and not self._error_handled:
            self._error_handled = True
            self._loading_error = True
            # Stop any current load
            self._web_view.stop()
            # Show our error page
            ErrorHandler.show_error_page(self._web_view, self._web_view.url().toString())

    # Override to prevent default error page and dialogs
    def javaScriptAlert(self, securityOrigin, msg):
        pass

    def javaScriptConfirm(self, securityOrigin, msg):
        return False

    def javaScriptPrompt(self, securityOrigin, msg, defaultValue):
        return False, ""

class RoundedWebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self._page = CustomWebEnginePage(self)
        self.setPage(self._page)

    def page(self):
        return self._page

    def paintEvent(self, event):
        if not self.window().isMaximized():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(self.rect(), 10, 10)
            painter.setClipPath(path)
            painter.setClipRegion(QRegion(self.rect(), QRegion.Rectangle))
            super().paintEvent(event)
        else:
            super().paintEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            hit_test_result = self.page().hitTestContent(event.pos())
            if hit_test_result.linkUrl().isValid():
                self.open_link_in_new_tab(hit_test_result.linkUrl())
                event.accept()
                return
        super().mousePressEvent(event)

    def open_link_in_new_tab(self, url: QUrl):
        self.window().add_new_tab(url)

def add_new_tab(tab_widget, url_bar, download_manager, qurl=None, label="New Tab"):
    browser = RoundedWebView()
    i = tab_widget.addTab(browser, label)
    tab_widget.setCurrentIndex(i)

    def update_tab_title():
        tab_widget.setTabText(i, browser.page().title())
        if browser == tab_widget.currentWidget():
            tab_widget.parent().setWindowTitle(f"KEPLER - {browser.page().title()}")

    browser.urlChanged.connect(lambda qurl, browser=browser: update_url(qurl, browser, url_bar))
    browser.loadFinished.connect(lambda _: QTimer.singleShot(0, update_tab_title))

    QTimer.singleShot(0, lambda: load_url(browser, qurl))
    return browser

def load_url(browser, qurl):
    if qurl:
        browser.page()._loading_error = False
        browser.setUrl(qurl)
    else:
        homepage_content = PageTemplates.get_homepage()
        base_url = QUrl.fromLocalFile(os.path.abspath('Images/'))
        browser.setHtml(homepage_content, base_url)

def update_url(qurl, browser, url_bar):
    if browser == browser.parent().currentWidget():
        url_bar.setText(qurl.toString())
