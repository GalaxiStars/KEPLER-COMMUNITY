import psutil
import os
import time
import threading
from PySide6.QtCore import QObject, Signal, QTimer
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='kepler_resource.log'
)
logger = logging.getLogger('ResourceManager')

class ResourceManager(QObject):
    resource_update = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.process = psutil.Process(os.getpid())
        self.network_limit = None
        self.cpu_limit = None
        self.memory_limit = None
        
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()
        
        # Initialize timers after moving to the main thread
        QTimer.singleShot(0, self.setup_timers)

    def setup_timers(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_resource_usage)
        self.update_timer.start(1000)  # Update every second

        self.enforce_timer = QTimer(self)
        self.enforce_timer.timeout.connect(self.enforce_limits)
        self.enforce_timer.start(500)  # Check limits every 500ms

    def set_cpu_limit(self, limit_percent):
        try:
            self.cpu_limit = limit_percent
            if limit_percent is not None:
                # Set process priority to below normal if CPU limit is set
                self.process.nice(10)  # Higher nice value = lower priority (Unix-like systems)
                logger.info(f"CPU limit set to {limit_percent}%")
        except Exception as e:
            logger.error(f"Failed to set CPU limit: {e}")

    def set_memory_limit(self, limit_mb):
        try:
            self.memory_limit = limit_mb
            if limit_mb is not None:
                # We'll enforce this in enforce_limits()
                logger.info(f"Memory limit set to {limit_mb}MB")
                
                # Set process priority to below normal
                try:
                    self.process.nice(10)
                    logger.info("Process priority adjusted")
                except Exception as e:
                    logger.warning(f"Failed to adjust process priority: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to set memory limit: {e}")

    def set_network_limit(self, limit_kbps):
        self.network_limit = limit_kbps * 1024 / 8 if limit_kbps else None
        logger.info(f"Network limit set to {limit_kbps} kbps")

    def enforce_limits(self):
        try:
            if self.memory_limit:
                current_memory = self.process.memory_info().rss / (1024 * 1024)
                if current_memory > self.memory_limit:
                    # Try to free some memory
                    self.process.nice(10)
                    logger.warning(f"Memory usage ({current_memory:.2f}MB) exceeded limit ({self.memory_limit}MB)")
                    
                    # Force garbage collection
                    import gc
                    gc.collect()
                    
            if self.cpu_limit:
                cpu_percent = self.process.cpu_percent()
                if cpu_percent > self.cpu_limit:
                    # Increase nice value to reduce CPU priority
                    current_nice = self.process.nice()
                    if current_nice < 19:  # Max nice value on Unix-like systems
                        self.process.nice(current_nice + 1)
                    logger.warning(f"CPU usage ({cpu_percent}%) exceeded limit ({self.cpu_limit}%)")
                
        except Exception as e:
            logger.error(f"Error enforcing limits: {e}")

    def update_resource_usage(self):
        try:
            current_time = time.time()
            current_net_io = psutil.net_io_counters()
            
            time_diff = current_time - self.last_time
            bytes_sent = current_net_io.bytes_sent - self.last_net_io.bytes_sent
            bytes_recv = current_net_io.bytes_recv - self.last_net_io.bytes_recv
            
            net_speed_sent = bytes_sent / time_diff if time_diff > 0 else 0
            net_speed_recv = bytes_recv / time_diff if time_diff > 0 else 0
            
            usage = {
                'cpu': self.process.cpu_percent(),
                'memory': self.process.memory_info().rss / (1024 * 1024),
                'network_sent': net_speed_sent / (1024 * 1024),
                'network_recv': net_speed_recv / (1024 * 1024)
            }
            
            self.last_time = current_time
            self.last_net_io = current_net_io
            
            self.resource_update.emit(usage)
            return usage
        except Exception as e:
            logger.error(f"Error updating resource usage: {e}")
            return None

    def get_current_usage(self):
        try:
            return {
                'cpu': self.process.cpu_percent(),
                'memory': self.process.memory_info().rss / (1024 * 1024),
                'network_sent': 0,
                'network_recv': 0
            }
        except Exception as e:
            logger.error(f"Error getting current usage: {e}")
            return None