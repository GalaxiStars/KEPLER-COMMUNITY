from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide6.QtCore import QObject, QTimer, QDateTime
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='kepler_network.log'
)
logger = logging.getLogger('NetworkManager')

class NetworkLimiter(QWebEngineUrlRequestInterceptor):
    def __init__(self, resource_manager):
        super().__init__()
        self.resource_manager = resource_manager
        self.last_request_time = QDateTime.currentMSecsSinceEpoch()
        self.bytes_processed = 0
        self.request_queue = []
        self.window_size = 1000  # 1 second window
        
        # Start cleanup timer after initialization
        QTimer.singleShot(0, self.setup_timer)

    def setup_timer(self):
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.cleanup_old_requests)
        self.cleanup_timer.start(1000)  # Cleanup every second

    def interceptRequest(self, info):
        try:
            current_time = QDateTime.currentMSecsSinceEpoch()
            
            # Clean up old requests
            self.cleanup_old_requests()
            
            if self.resource_manager.network_limit:
                # Estimate request size based on URL and method
                estimated_size = self.estimate_request_size(info)
                
                # Calculate current bandwidth usage
                current_bandwidth = self.calculate_current_bandwidth()
                
                # If we're over the limit, delay the request
                if current_bandwidth + estimated_size > self.resource_manager.network_limit:
                    delay = self.calculate_delay(estimated_size)
                    if delay > 0:
                        time.sleep(delay)
                
                # Record the request
                self.request_queue.append({
                    'time': current_time,
                    'size': estimated_size
                })
                
                logger.info(f"Request processed: {info.requestUrl().toString()[:100]}... "
                           f"Size: {estimated_size/1024:.2f}KB, "
                           f"Current bandwidth: {current_bandwidth/1024:.2f}KB/s")
            
            # Always allow the request
            info.block(False)
            
        except Exception as e:
            logger.error(f"Error in interceptRequest: {e}")
            info.block(False)  # Allow request in case of error

    def estimate_request_size(self, info):
        # Estimate size based on request type and URL
        url = info.requestUrl().toString().lower()
        method = info.requestMethod().data().decode().upper()
        
        if method == "GET":
            if any(ext in url for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                return 500 * 1024  # 500KB for images
            elif any(ext in url for ext in ['.mp4', '.webm', '.m3u8']):
                return 2 * 1024 * 1024  # 2MB for video
            elif any(ext in url for ext in ['.mp3', '.wav']):
                return 1 * 1024 * 1024  # 1MB for audio
            elif any(ext in url for ext in ['.css', '.js']):
                return 50 * 1024  # 50KB for scripts and styles
            else:
                return 100 * 1024  # 100KB default for other GET requests
        elif method == "POST":
            return 200 * 1024  # 200KB for POST requests
        else:
            return 50 * 1024  # 50KB for other methods

    def calculate_current_bandwidth(self):
        current_time = QDateTime.currentMSecsSinceEpoch()
        window_start = current_time - self.window_size
        
        # Sum up all requests in the current window
        total_bytes = sum(req['size'] for req in self.request_queue 
                         if req['time'] > window_start)
        
        return total_bytes / (self.window_size / 1000)  # Convert to bytes per second

    def calculate_delay(self, request_size):
        if not self.resource_manager.network_limit:
            return 0
            
        current_bandwidth = self.calculate_current_bandwidth()
        if current_bandwidth + request_size > self.resource_manager.network_limit:
            # Calculate how long to wait for bandwidth to become available
            excess_bytes = current_bandwidth + request_size - self.resource_manager.network_limit
            return excess_bytes / self.resource_manager.network_limit
        return 0

    def cleanup_old_requests(self):
        current_time = QDateTime.currentMSecsSinceEpoch()
        window_start = current_time - self.window_size
        
        # Remove requests older than the window
        self.request_queue = [req for req in self.request_queue 
                            if req['time'] > window_start]

class ThrottledNetworkManager(QObject):
    def __init__(self, resource_manager):
        super().__init__()
        self.resource_manager = resource_manager
        self.limiter = NetworkLimiter(resource_manager)
        logger.info("ThrottledNetworkManager initialized")

    def get_interceptor(self):
        return self.limiter