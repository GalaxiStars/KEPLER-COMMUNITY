import psutil
import os
import time
import threading
from PySide6.QtCore import QObject, Signal, QTimer
import win32job
import win32process
import win32api
import win32con
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='kepler_resource.log'
)
logger = logging.getLogger('ResourceManager')

# Windows-specific job object constants
JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_WORKINGSET = 0x00000001
JOB_OBJECT_LIMIT_PROCESS_TIME = 0x00000002
JOB_OBJECT_CPU_RATE_CONTROL = 0x00000004

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
        
        try:
            # Create a new job object
            security_attributes = None
            self.job = win32job.CreateJobObject(security_attributes, f"KEPLER_JOB_{os.getpid()}")
            
            # Set up basic limits with all required fields
            job_info = {
                'BasicLimitInformation': {
                    'PerProcessUserTimeLimit': 0,
                    'PerJobUserTimeLimit': 0,
                    'LimitFlags': (JOB_OBJECT_LIMIT_PROCESS_MEMORY | 
                                 JOB_OBJECT_LIMIT_JOB_MEMORY |
                                 JOB_OBJECT_LIMIT_WORKINGSET),
                    'MinimumWorkingSetSize': 0,
                    'MaximumWorkingSetSize': 0,
                    'ActiveProcessLimit': 0,
                    'Affinity': 0,
                    'PriorityClass': 0,
                    'SchedulingClass': 0
                }
            }
            
            win32job.SetInformationJobObject(
                self.job,
                win32job.JobObjectBasicLimitInformation,
                job_info
            )
            
            logger.info("Job object created successfully")
            self.assign_process_to_job()
        except Exception as e:
            logger.error(f"Failed to create job object: {e}")
            self.job = None

        # Initialize timers after moving to the main thread
        QTimer.singleShot(0, self.setup_timers)

    def setup_timers(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_resource_usage)
        self.update_timer.start(1000)  # Update every second

        self.enforce_timer = QTimer(self)
        self.enforce_timer.timeout.connect(self.enforce_limits)
        self.enforce_timer.start(500)  # Check limits every 500ms

    def assign_process_to_job(self):
        if not self.job:
            logger.error("No job object available")
            return False

        try:
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, os.getpid())
            win32job.AssignProcessToJobObject(self.job, handle)
            win32api.CloseHandle(handle)
            logger.info("Process assigned to job object successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to assign process to job: {e}")
            return False

    def set_cpu_limit(self, limit_percent):
        try:
            self.cpu_limit = limit_percent
            if self.job and limit_percent is not None:
                # Convert percentage to CPU cycles (1% = 100 cycles)
                cpu_rate = int(limit_percent * 100)
                
                job_info = {
                    'BasicLimitInformation': {
                        'PerProcessUserTimeLimit': 0,
                        'PerJobUserTimeLimit': 0,
                        'LimitFlags': JOB_OBJECT_CPU_RATE_CONTROL,
                        'MinimumWorkingSetSize': 0,
                        'MaximumWorkingSetSize': 0,
                        'ActiveProcessLimit': 0,
                        'Affinity': 0,
                        'PriorityClass': 0,
                        'SchedulingClass': 0
                    },
                    'CpuRate': cpu_rate
                }
                
                win32job.SetInformationJobObject(
                    self.job,
                    win32job.JobObjectBasicLimitInformation,
                    job_info
                )
                logger.info(f"CPU limit set to {limit_percent}%")
        except Exception as e:
            logger.error(f"Failed to set CPU limit: {e}")

    def set_memory_limit(self, limit_mb):
        try:
            self.memory_limit = limit_mb
            if self.job and limit_mb is not None:
                limit_bytes = limit_mb * 1024 * 1024  # Convert MB to bytes
                
                job_info = {
                    'BasicLimitInformation': {
                        'PerProcessUserTimeLimit': 0,
                        'PerJobUserTimeLimit': 0,
                        'LimitFlags': (JOB_OBJECT_LIMIT_PROCESS_MEMORY | 
                                     JOB_OBJECT_LIMIT_JOB_MEMORY |
                                     JOB_OBJECT_LIMIT_WORKINGSET),
                        'MinimumWorkingSetSize': 0,
                        'MaximumWorkingSetSize': limit_bytes,
                        'ActiveProcessLimit': 0,
                        'Affinity': 0,
                        'PriorityClass': 0,
                        'SchedulingClass': 0
                    },
                    'JobMemoryLimit': limit_bytes,
                    'ProcessMemoryLimit': limit_bytes
                }
                
                win32job.SetInformationJobObject(
                    self.job,
                    win32job.JobObjectExtendedLimitInformation,
                    job_info
                )
                
                logger.info(f"Memory limit set to {limit_mb}MB ({limit_bytes} bytes)")
                
                # Also set process priority
                try:
                    self.process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
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
                    self.process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    logger.warning(f"Memory usage ({current_memory:.2f}MB) exceeded limit ({self.memory_limit}MB)")
                    
                    # Force garbage collection
                    import gc
                    gc.collect()
                    
                    # Try to reduce working set
                    try:
                        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, os.getpid())
                        win32process.SetProcessWorkingSetSize(handle, -1, -1)
                        win32api.CloseHandle(handle)
                    except Exception as e:
                        logger.error(f"Failed to reduce working set: {e}")
                else:
                    self.process.nice(psutil.NORMAL_PRIORITY_CLASS)
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

    def __del__(self):
        try:
            if self.job:
                win32job.TerminateJobObject(self.job, 0)
        except Exception as e:
            logger.error(f"Error cleaning up job object: {e}")