from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from error_handling import ErrorHandler

class ProtocolHandler:
    @staticmethod
    def handle_url(browser, url_text: str):
        """Handle URL navigation with proper protocol selection."""
        url_text = url_text.strip()
        
        # Handle URLs without protocol
        if not url_text.startswith(('http://', 'https://', 'file://')):
            # Check if it's a valid domain
            if '.' in url_text and not url_text.startswith('javascript:'):
                ErrorHandler.try_protocols(browser, url_text)
                return True
            else:
                # If no dot, treat as a search query
                url_text = f'https://www.google.com/search?q={url_text}'
        
        # Create QUrl object
        q = QUrl(url_text)
        
        # Ensure the scheme is set and valid
        if not q.scheme():
            q.setScheme('https')
        
        # Validate the URL
        if not q.isValid():
            # If invalid, try as a search query
            search_url = f'https://www.google.com/search?q={url_text}'
            q = QUrl(search_url)
        
        current_widget = browser.tab_widget.currentWidget()
        if current_widget:
            def handle_navigation_result(ok):
                if not ok:
                    ErrorHandler.show_error_page(current_widget, url_text)
                try:
                    current_widget.loadFinished.disconnect(handle_navigation_result)
                except:
                    pass

            try:
                current_widget.loadFinished.disconnect()
            except:
                pass
            current_widget.loadFinished.connect(handle_navigation_result)
            current_widget.setUrl(q)
            return True
        else:
            print("No current tab to navigate")
            return False

    @staticmethod
    def try_protocols(browser, domain: str):
        """Try connecting to a domain using different protocols."""
        ErrorHandler.try_protocols(browser, domain)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if the given URL is valid."""
        url = QUrl(url)
        return url.isValid()

    @staticmethod
    def ensure_protocol(url: str) -> str:
        """Ensure URL has a protocol, defaulting to HTTPS."""
        if not url.startswith(('http://', 'https://', 'file://')):
            return f'https://{url}'
        return url 