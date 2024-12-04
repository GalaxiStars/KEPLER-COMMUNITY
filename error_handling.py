from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from page_templates import PageTemplates
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='kepler_error.log'
)
logger = logging.getLogger('ErrorHandler')

class ErrorHandler:
    @staticmethod
    def show_error_page(web_view: QWebEngineView, domain: str):
        """Display a custom error page when a connection fails."""
        try:
            # Safely disconnect any existing loadFinished signals
            try:
                web_view.loadFinished.disconnect()
            except TypeError:
                pass

            # Stop any current load
            web_view.stop()
            
            # Clear the page immediately
            web_view.setHtml("")
            
            # Disable error page handling in settings
            profile = web_view.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, False)
            
            # Show our custom error page immediately
            PageTemplates.show_error_page(web_view, domain)
            
            logger.info(f"Showing error page for domain: {domain}")
        except Exception as e:
            logger.error(f"Error showing error page: {e}")

    @staticmethod
    def try_protocols(browser, domain: str):
        """Try connecting to a domain using different protocols."""
        current_widget = browser.tab_widget.currentWidget()
        if not current_widget:
            logger.warning("No current widget found")
            return

        # Safely disconnect any existing signals
        try:
            current_widget.loadFinished.disconnect()
        except TypeError:
            pass

        def try_https():
            https_url = QUrl(f'https://{domain}')
            
            def handle_https_result(ok):
                if not ok:
                    try_http()
                try:
                    current_widget.loadFinished.disconnect(handle_https_result)
                except TypeError:
                    pass

            current_widget.loadFinished.connect(handle_https_result)
            current_widget.setUrl(https_url)
            logger.info(f"Trying HTTPS for domain: {domain}")

        def try_http():
            try:
                current_widget.loadFinished.disconnect()
            except TypeError:
                pass

            http_url = QUrl(f'http://{domain}')
            
            def handle_http_result(ok):
                if not ok:
                    ErrorHandler.show_error_page(current_widget, domain)
                try:
                    current_widget.loadFinished.disconnect(handle_http_result)
                except TypeError:
                    pass

            current_widget.loadFinished.connect(handle_http_result)
            current_widget.setUrl(http_url)
            logger.info(f"Trying HTTP for domain: {domain}")

        # Start with HTTPS
        try_https() 