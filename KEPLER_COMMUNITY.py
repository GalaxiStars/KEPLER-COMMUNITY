import sys
import os
from PySide6.QtCore import QUrl, Qt, QSize, QOperatingSystemVersion, QTimer
from PySide6.QtGui import QIcon, QPixmap, QAction, QPainter, QPainterPath, QRegion, QColor, QCursor
from PySide6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineSettings
)
from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QToolBar, QPushButton, QTabWidget, QWidget, QHBoxLayout, QLabel, QMenu, QInputDialog, QDialog, QTabBar, QMenu, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QMessageBox, QSizePolicy
from PySide6.QtWebEngineWidgets import QWebEngineView
from functools import partial
from custom_dialog import CustomInputDialog, DraggableTitle, ResourceDialog
from error_handling import ErrorHandler
from protocol_handler import ProtocolHandler
from page_templates import PageTemplates

from download_manager import DownloadManager
from microphone_manager import MicrophoneManager
from tab_manager import add_new_tab, RoundedWebView
from styles import get_main_window_style, get_toolbar_style, get_button_style, get_line_edit_style, get_bookmark_menu_style, get_bookmark_header_style
from event_handler import DraggableTitleBar
from bookmark_manager import BookmarkManager
from resource_manager import ResourceManager
from custom_network_manager import ThrottledNetworkManager
from fingerprint_manager import FingerprintManager

class CustomTabBar(QTabBar):
    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            index = self.tabAt(event.position().toPoint())
            if index != -1:
                self.parent().parent().close_current_tab(index)
        super().mousePressEvent(event)

class CustomBookmarkMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(get_bookmark_menu_style())
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(2)
        
        # Create a container widget for bookmarks
        self.bookmark_container = QWidget()
        self.bookmark_layout = QVBoxLayout(self.bookmark_container)
        self.bookmark_layout.setContentsMargins(0, 0, 0, 0)
        self.bookmark_layout.setSpacing(2)
        
        # Header
        header = QLabel("Bookmarks")
        header.setStyleSheet(get_bookmark_header_style())
        self.layout.addWidget(header)
        
        # Add bookmark container to main layout
        self.layout.addWidget(self.bookmark_container)

        # Set a minimum width but allow expansion
        self.setMinimumWidth(300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

    def clear_bookmarks(self):
        # Clear all bookmark items from the container
        while self.bookmark_layout.count():
            item = self.bookmark_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def refresh_bookmarks(self, bookmarks, callbacks):
        # Clear existing bookmarks
        self.clear_bookmarks()
        
        # Add updated bookmarks
        for bookmark in bookmarks:
            bookmark_id, title, url = bookmark
            self.add_bookmark_item(title, url, bookmark_id, callbacks)

    def add_bookmark_item(self, title, url, bookmark_id, callbacks):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(2, 2, 2, 2)
        
        # Main button for opening bookmark
        open_btn = QPushButton(title)
        open_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        open_btn.clicked.connect(lambda: callbacks['open'](url))
        item_layout.addWidget(open_btn)
        
        # Action buttons container
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(4)
        
        # Edit button
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon('Images/edit-64.png'))
        edit_btn.setFixedSize(24, 24)
        edit_btn.clicked.connect(lambda: callbacks['rename'](bookmark_id))
        action_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon('Images/delete-64.png'))
        delete_btn.setFixedSize(24, 24)
        delete_btn.clicked.connect(lambda: callbacks['delete'](bookmark_id))
        action_layout.addWidget(delete_btn)
        
        item_layout.addWidget(action_widget)
        self.bookmark_layout.addWidget(item_widget)

    def show_menu(self, button):
        # Calculate position to show below the button
        button_pos = button.mapToGlobal(button.rect().bottomLeft())
        menu_width = max(300, button.width() * 2)  # Make menu at least as wide as two buttons
        
        # Ensure menu doesn't go off screen
        screen = QApplication.primaryScreen().geometry()
        x_pos = min(button_pos.x(), screen.right() - menu_width)
        y_pos = button_pos.y()
        
        # Set the menu width
        self.setFixedWidth(menu_width)
        
        # Move and show the menu
        self.move(x_pos, y_pos)
        self.show()
        
    def mousePressEvent(self, event):
        if not self.geometry().contains(event.globalPosition().toPoint()):
            self.hide()

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KEPLER COMMUNITY")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(get_main_window_style())
        # Remove transparency
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Set frameless window hint
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.download_manager = DownloadManager()
        self.microphone_manager = MicrophoneManager()
        self.bookmark_manager = BookmarkManager()
        self.resource_manager = ResourceManager()
        
        # Set custom User-Agent
        profile = QWebEngineProfile.defaultProfile()
        
        # Determine the Windows version first
        os_version = QOperatingSystemVersion.current()
        if os_version >= QOperatingSystemVersion.Windows11:
            windows_version = "Windows NT 10.0"
        elif os_version >= QOperatingSystemVersion.Windows10:
            windows_version = "Windows NT 10.0"
        else:
            windows_version = "Windows NT 6.1"  # Default to Windows 7 for older versions

        # Create custom user agent
        custom_user_agent = f"KEPLER COMMUNITY/1.0 Mozilla/5.0 ({windows_version}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # Disable telemetry and data collection
        settings = profile.settings()
        
        # Privacy-focused settings
        profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)  # Cache in memory only
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)  # Don't save cookies
        profile.setHttpUserAgent(custom_user_agent)  # Use custom user agent
        profile.setHttpAcceptLanguage("en-US,en;q=0.9")
        
        # Disable all tracking and telemetry features
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, True)  # Prevent WebRTC from exposing local IPs
        settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, False)  # Disable DNS prefetching
        settings.setAttribute(QWebEngineSettings.HyperlinkAuditingEnabled, False)  # Disable ping tracking
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)  # Keep images but load from cache
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, False)  # Use our custom error pages
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, False)  # Disable built-in PDF viewer
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, False)  # Disable screen capture
        settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, False)  # Block geolocation
        settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, False)  # Prevent automatic focus
        
        # Configure cross-origin settings
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.ShowScrollBars, True)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)
        settings.setAttribute(QWebEngineSettings.TouchIconsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
        settings.setAttribute(QWebEngineSettings.PrintElementBackgrounds, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)  # Only for development
        
        # Enable JavaScript, Cookies, and WebRTC
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, False)
        
        # Disable Google services and safebrowsing
        os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "0"  # Keep sandbox enabled
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-driver-bug-workarounds"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-breakpad"  # Disable crash reporting
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=OptimizationHints"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=MediaRouter"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=NetworkService"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=AudioServiceOutOfProcess"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-speech-api"  # Disable speech recognition
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-background-networking"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-component-update"  # Prevent auto-updates
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-default-apps"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-sync"  # Disable Chrome Sync
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-translate"  # Disable Google Translate
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-webrtc-hw-encoding"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-client-side-phishing-detection"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=AutofillServerCommunication"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=Translate"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=ChromeWhatsNew"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=SafetyCheck"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=ChromeCart"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=TabGroups"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=TabHoverCards"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=DesktopPWAs"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=WebOTP"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=WebPayments"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=WebUSB"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=WebXR"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --disable-features=WebAuthentication"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --no-pings"  # Disable hyperlink auditing
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --no-proxy-server"  # Disable proxy
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --no-service-autorun"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --safebrowsing-disable-auto-update"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --safebrowsing-disable-download-protection"

        # Additional privacy-focused profile settings
        profile.setPersistentStoragePath("")  # Disable persistent storage by setting empty path
        profile.setHttpCacheType(QWebEngineProfile.NoCache)  # Disable HTTP cache
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)  # Disable persistent cookies
        profile.clearAllVisitedLinks()  # Clear any visited links
        profile.clearHttpCache()  # Clear HTTP cache
        
        # Additional privacy-focused settings
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)  # Prevent fullscreen tracking
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, False)  # Block insecure content
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, False)  # Prevent window activation tracking
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)  # Disable local storage
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, True)  # Strict WebRTC
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)  # Prevent clipboard access
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, False)  # Disable WebGL
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, False)  # Disable scroll animations
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)  # Disable plugins
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, False)  # Disable PDF viewer

        # Initialize fingerprint manager
        self.fingerprint_manager = FingerprintManager()
        
        # Get JavaScript code for fingerprint randomization
        self.anti_fingerprint_js = self.fingerprint_manager.apply_fingerprint(profile, settings)
        
        # Set up timer for periodic fingerprint rotation
        self.fingerprint_timer = QTimer(self)
        self.fingerprint_timer.timeout.connect(self.rotate_fingerprint)
        self.fingerprint_timer.start(1800000)  # Rotate every 30 minutes
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(CustomTabBar())
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_current_tab)
        self.tab_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)
        self.setCentralWidget(self.tab_widget)

        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet(get_toolbar_style())
        self.addToolBar(self.toolbar)

        self.add_navigation_buttons()
        self.add_url_bar()

        # Check if the current OS is Windows 10
        self.is_windows_10 = QOperatingSystemVersion.current() == QOperatingSystemVersion.Windows10

        # Use a timer to defer loading of the first tab
        QTimer.singleShot(0, self.load_initial_tab)

        self.init_title_bar()

        # Set up the custom network manager
        self.network_manager = ThrottledNetworkManager(self.resource_manager)
        profile.setUrlRequestInterceptor(self.network_manager.get_interceptor())

        self.resource_update_timer = QTimer(self)
        self.resource_update_timer.timeout.connect(self.update_resource_usage)
        self.resource_update_timer.start(1000)  # Update every second

        # Connect the tab changed signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.resource_limits = {'cpu': 100, 'memory': 0, 'network': 0}

        # Add this line to make the add_new_tab method accessible to RoundedWebView
        RoundedWebView.open_link_in_new_tab = self.add_new_tab

        # Connect to bookmark manager signals
        self.bookmark_manager.bookmarks_updated.connect(self.on_bookmarks_updated)
        self.current_bookmark_menu = None  # Keep track of the current menu

        self.setup_privacy_timer()

    def init_title_bar(self):
        self.title_bar = DraggableTitleBar(self)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setStyleSheet("background-color: #240970;")

        self.title_bar_layout = QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar_layout.setSpacing(0)

        self.title_icon = QLabel(self.title_bar)
        self.title_icon.setPixmap(QPixmap('Images/KEPLER-COMMUNITY-ICO.png').scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.title_bar_layout.addWidget(self.title_icon)

        self.title_label = QLabel("KEPLER COMMUNITY [ALPHA]", self.title_bar)
        self.title_label.setStyleSheet("color: white; padding: 5px; font-size: 16px; font-weight: bold; font-family: 'Trebuchet MS', sans-serif;")
        self.title_bar_layout.addWidget(self.title_label)

        self.title_bar_layout.addStretch()

        minimize_btn = QPushButton(self.title_bar)
        minimize_btn.setIcon(QIcon('Images/minimize-64.png'))
        minimize_btn.setIconSize(QSize(24, 24))
        minimize_btn.setStyleSheet(get_button_style())
        minimize_btn.clicked.connect(self.showMinimized)
        self.title_bar_layout.addWidget(minimize_btn)

        self.maximize_btn = QPushButton(self.title_bar)
        self.maximize_btn.setIcon(QIcon('Images/maximize-64.png'))
        self.maximize_btn.setIconSize(QSize(24, 24))
        self.maximize_btn.setStyleSheet(get_button_style())
        self.maximize_btn.clicked.connect(self.toggle_maximize_restore)
        self.title_bar_layout.addWidget(self.maximize_btn)

        close_btn = QPushButton(self.title_bar)
        close_btn.setIcon(QIcon('Images/close-64.png'))
        close_btn.setIconSize(QSize(24, 24))
        close_btn.setStyleSheet(get_button_style())
        close_btn.clicked.connect(self.close)
        self.title_bar_layout.addWidget(close_btn)

        self.setMenuWidget(self.title_bar)

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setIcon(QIcon('Images/maximize-64.png'))
        else:
            self.showMaximized()
            self.maximize_btn.setIcon(QIcon('Images/restore-64.png'))
            self.clearMask()

    def showNormal(self):
        super().showNormal()
        self.resize(1200, 800)  # Reset to original size
        self.maximize_btn.setIcon(QIcon('Images/maximize-64.png'))
        if not self.is_windows_10:
            self.setMask(self.roundedMask())

    def add_navigation_buttons(self):
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(5)

        back_btn = QPushButton()
        back_btn.setIcon(QIcon('Images/return-64.png'))
        back_btn.setIconSize(QSize(24, 24))
        back_btn.setStyleSheet(get_button_style())
        back_btn.clicked.connect(lambda: self.tab_widget.currentWidget().back())
        nav_layout.addWidget(back_btn)

        forward_btn = QPushButton()
        forward_btn.setIcon(QIcon('Images/forward-64.png'))
        forward_btn.setIconSize(QSize(24, 24))
        forward_btn.setStyleSheet(get_button_style())
        forward_btn.clicked.connect(lambda: self.tab_widget.currentWidget().forward())
        nav_layout.addWidget(forward_btn)

        reload_btn = QPushButton()
        reload_btn.setIcon(QIcon('Images/refresh-64.png'))
        reload_btn.setIconSize(QSize(24, 24))
        reload_btn.setStyleSheet(get_button_style())
        reload_btn.clicked.connect(lambda: self.tab_widget.currentWidget().reload())
        nav_layout.addWidget(reload_btn)

        home_btn = QPushButton()
        home_btn.setIcon(QIcon('Images/home-page-64.png'))
        home_btn.setIconSize(QSize(24, 24))
        home_btn.setStyleSheet(get_button_style())
        home_btn.clicked.connect(lambda: self.load_homepage())
        nav_layout.addWidget(home_btn)

        new_tab_button = QPushButton()
        new_tab_button.setIcon(QIcon('Images/add-new-64.png'))
        new_tab_button.setIconSize(QSize(24, 24))
        new_tab_button.setStyleSheet(get_button_style())
        new_tab_button.clicked.connect(lambda: self.add_new_tab())
        nav_layout.addWidget(new_tab_button)

        resource_btn = QPushButton()
        resource_btn.setIcon(QIcon('Images/resource-64.png'))
        resource_btn.setIconSize(QSize(24, 24))
        resource_btn.setStyleSheet(get_button_style())
        resource_btn.clicked.connect(self.show_resource_dialog)
        nav_layout.addWidget(resource_btn)

        self.toolbar.addWidget(nav_widget)

    def load_homepage(self):
        """Load the homepage in the current tab."""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            homepage_content = PageTemplates.get_homepage()
            base_url = QUrl.fromLocalFile(os.path.abspath('Images/'))
            current_widget.setHtml(homepage_content, base_url)

    def load_initial_tab(self):
        """Load the initial tab with homepage."""
        self.add_new_tab(None, "Homepage")

    def add_new_tab(self, qurl=None, label="New Tab"):
        """Add a new tab with the given URL or homepage if none provided."""
        browser = add_new_tab(self.tab_widget, self.url_bar, self.download_manager, qurl, label)
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(browser, title))
        browser.page().featurePermissionRequested.connect(self.handle_permission_request)
        
        # Inject anti-fingerprinting JavaScript
        browser.page().loadFinished.connect(
            lambda: browser.page().runJavaScript(self.anti_fingerprint_js)
        )
        
        # Set the new tab as the current tab
        self.tab_widget.setCurrentWidget(browser)
        
        # Ensure the web view is properly sized
        QTimer.singleShot(0, lambda: self.resize_web_view(browser))

        return browser

    def add_url_bar(self):
        url_widget = QWidget()
        url_layout = QHBoxLayout(url_widget)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(5)

        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet(get_line_edit_style())
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        url_layout.addWidget(self.url_bar)

        # Add to Bookmarks button
        add_bookmark_btn = QPushButton()
        add_bookmark_btn.setIcon(QIcon('Images/bookmark-64.png'))
        add_bookmark_btn.setIconSize(QSize(24, 24))
        add_bookmark_btn.setStyleSheet(get_button_style())
        add_bookmark_btn.clicked.connect(self.add_bookmark)
        url_layout.addWidget(add_bookmark_btn)

        # Bookmark Menu button
        bookmark_menu_btn = QPushButton()
        bookmark_menu_btn.setIcon(QIcon('Images/bookmark-menu-64.png'))
        bookmark_menu_btn.setIconSize(QSize(24, 24))
        bookmark_menu_btn.setStyleSheet(get_button_style())
        bookmark_menu_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        bookmark_menu_btn.customContextMenuRequested.connect(self.show_bookmark_menu)
        bookmark_menu_btn.clicked.connect(lambda: self.show_bookmark_menu(bookmark_menu_btn))
        url_layout.addWidget(bookmark_menu_btn)

        self.toolbar.addWidget(url_widget)

    def update_tab_title(self, browser, title):
        index = self.tab_widget.indexOf(browser)
        if index >= 0:
            self.tab_widget.setTabText(index, title)
            if browser == self.tab_widget.currentWidget():
                self.setWindowTitle(f"KEPLER COMMUNITY - {title}")

    def resize_web_view(self, browser):
        browser.setGeometry(self.tab_widget.contentsRect())
        if not self.isMaximized() and not self.is_windows_10:
            path = QPainterPath()
            path.addRoundedRect(browser.rect(), 10, 10)
            browser.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def navigate_to_url(self):
        ProtocolHandler.handle_url(self, self.url_bar.text())

    def update_window_title(self, index=None):
        if index is None:
            index = self.tab_widget.currentIndex()
        if index >= 0:
            current_browser = self.tab_widget.widget(index)
            page_title = current_browser.title()
            self.setWindowTitle(f"KEPLER COMMUNITY - {page_title}")
        else:
            self.setWindowTitle("KEPLER COMMUNITY")

    def close_current_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def handle_permission_request(self, origin, feature):
        if feature == QWebEnginePage.Feature.MediaAudioCapture:
            return self.microphone_manager.handle_permission_request(origin, feature)
        return False

    def add_bookmark(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            dialog = CustomInputDialog(self, "Add Bookmark", "Enter bookmark name:", current_browser.title())
            if dialog.exec() == QDialog.Accepted:
                title = dialog.get_input()
                if title:
                    url = current_browser.url().toString()
                    self.bookmark_manager.add_bookmark(title, url)

    def rename_bookmark(self, bookmark_id):
        bookmarks = self.bookmark_manager.get_bookmarks()
        for bookmark in bookmarks:
            if bookmark[0] == bookmark_id:
                current_title = bookmark[1]
                dialog = CustomInputDialog(self, "Rename Bookmark", "Enter new name:", current_title)
                if dialog.exec() == QDialog.Accepted:
                    new_title = dialog.get_input()
                    if new_title:
                        self.bookmark_manager.rename_bookmark(bookmark_id, new_title)
                break

    def delete_bookmark(self, bookmark_id):
        self.bookmark_manager.remove_bookmark(bookmark_id)

    def open_bookmark(self, url):
        self.add_new_tab(QUrl(url), "Bookmark")

    def show_tab_context_menu(self, position):
        menu = QMenu(self)
        index = self.tab_widget.tabBar().tabAt(position)
        
        if index >= 0:
            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(lambda: self.rename_tab(index))
            menu.addAction(rename_action)
            
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.close_current_tab(index))
            menu.addAction(delete_action)
        
        menu.exec(self.tab_widget.mapToGlobal(position))

    def rename_tab(self, index):
        if index >= 0:
            current_title = self.tab_widget.tabText(index)
            new_title, ok = QInputDialog.getText(self, "Rename Tab", "Enter new name:", text=current_title)
            if ok and new_title:
                self.tab_widget.setTabText(index, new_title)

    def paintEvent(self, event):
        if not self.isMaximized() and not self.is_windows_10:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            path = QPainterPath()
            path.addRoundedRect(self.rect(), 10, 10)
            
            painter.setClipPath(path)
            painter.fillPath(path, QColor("#240970"))
        else:
            super().paintEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.isMaximized() and not self.is_windows_10:
            self.setMask(self.roundedMask())
        else:
            self.clearMask()
        
        # Update the web view's size and mask
        current_tab = self.tab_widget.currentWidget()
        if current_tab and isinstance(current_tab, RoundedWebView):
            current_tab.setGeometry(self.tab_widget.contentsRect())
            if not self.isMaximized() and not self.is_windows_10:
                path = QPainterPath()
                path.addRoundedRect(current_tab.rect(), 10, 10)
                current_tab.setMask(QRegion(path.toFillPolygon().toPolygon()))
            else:
                current_tab.clearMask()

    def showEvent(self, event):
        super().showEvent(event)
        # Force a resize event after the window is shown
        self.resizeEvent(None)

    def roundedMask(self):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)
        return QRegion(path.toFillPolygon().toPolygon())

    def show_resource_dialog(self):
        dialog = ResourceDialog(self, self.resource_limits)
        if dialog.exec() == QDialog.Accepted:
            cpu_limit = dialog.cpu_spinbox.value()
            memory_limit = dialog.memory_spinbox.value()
            network_limit = dialog.network_spinbox.value()
            
            self.resource_manager.set_cpu_limit(cpu_limit)
            self.resource_manager.set_memory_limit(memory_limit)
            self.resource_manager.set_network_limit(network_limit)

            # Save the new limits
            self.resource_limits = {
                'cpu': cpu_limit,
                'memory': memory_limit,
                'network': network_limit
            }

    def update_resource_usage(self):
        usage = self.resource_manager.get_current_usage()
        self.statusBar().showMessage(
            f"CPU: {usage['cpu']:.1f}% | "
            f"Memory: {usage['memory']:.1f} MB | "
            f"Network: ↑{usage['network_sent']:.2f} MB ↓{usage['network_recv']:.2f} MB"
        )

    def suspend_inactive_tabs(self):
        current_index = self.tab_widget.currentIndex()
        for i in range(self.tab_widget.count()):
            if i != current_index:
                web_view = self.tab_widget.widget(i)
                web_view.page().setLifecycleState(QWebEnginePage.LifecycleState.Frozen)

    def on_tab_changed(self, index):
        self.suspend_inactive_tabs()
        web_view = self.tab_widget.widget(index)
        web_view.page().setLifecycleState(QWebEnginePage.LifecycleState.Active)

    def closeEvent(self, event):
        super().closeEvent(event)

    def show_bookmark_menu(self, widget=None):
        if isinstance(widget, bool):  # Handle case when called directly
            widget = self.sender()  # Get the button that triggered the action
        
        # Create custom menu
        self.current_bookmark_menu = CustomBookmarkMenu(self)
        
        # Add bookmarks to the menu
        bookmarks = self.bookmark_manager.get_bookmarks()
        callbacks = {
            'open': self.open_bookmark,
            'rename': self.rename_bookmark,
            'delete': self.delete_bookmark
        }
        self.current_bookmark_menu.refresh_bookmarks(bookmarks, callbacks)
        
        # Show the menu below the button
        self.current_bookmark_menu.show_menu(widget)

    def on_bookmarks_updated(self):
        # Refresh the current bookmark menu if it exists and is visible
        if self.current_bookmark_menu and self.current_bookmark_menu.isVisible():
            bookmarks = self.bookmark_manager.get_bookmarks()
            callbacks = {
                'open': self.open_bookmark,
                'rename': self.rename_bookmark,
                'delete': self.delete_bookmark
            }
            self.current_bookmark_menu.refresh_bookmarks(bookmarks, callbacks)

    def setup_privacy_timer(self):
        self.privacy_timer = QTimer(self)
        self.privacy_timer.timeout.connect(self.clear_private_data)
        self.privacy_timer.start(300000)  # Clear every 5 minutes

    def clear_private_data(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearAllVisitedLinks()
        profile.clearHttpCache()
        profile.cookieStore().deleteAllCookies()
        
        # Force garbage collection
        import gc
        gc.collect()

    def rotate_fingerprint(self):
        """Periodically rotate the browser fingerprint"""
        profile = QWebEngineProfile.defaultProfile()
        settings = profile.settings()
        self.anti_fingerprint_js = self.fingerprint_manager.apply_fingerprint(profile, settings)
        
        # Apply new fingerprint to all existing tabs
        for i in range(self.tab_widget.count()):
            browser = self.tab_widget.widget(i)
            if isinstance(browser, RoundedWebView):
                browser.page().runJavaScript(self.anti_fingerprint_js)

if __name__ == '__main__':
    resource_manager = ResourceManager()
    resource_manager.assign_process_to_job()

    app = QApplication([])
    app.setApplicationName("KEPLER COMMUNITY")
    window = Browser()
    window.show()
    app.exec()

