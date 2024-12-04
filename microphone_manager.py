import pyaudio
import threading
import atexit
import numpy as np
from PySide6.QtWebEngineCore import QWebEnginePage
from collections import deque

class MicrophoneRecorder(object):
    def __init__(self, rate=44100, chunksize=1024, max_frames=100):
        self.rate = rate
        self.chunksize = chunksize
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunksize,
                                  stream_callback=self.new_frame)
        self.lock = threading.Lock()
        self.stop = False
        self.frames = deque(maxlen=max_frames)
        atexit.register(self.close)

    def new_frame(self, data, frame_count, time_info, status):
        data = np.frombuffer(data, dtype=np.int16)
        with self.lock:
            self.frames.append(data)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue
    
    def get_frames(self):
        with self.lock:
            return list(self.frames)
    
    def start(self):
        self.stream.start_stream()

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()
        self.p.terminate()

class MicrophoneManager:
    def __init__(self):
        self.microphone = None

    def start_microphone(self):
        self.microphone = MicrophoneRecorder()
        self.microphone.start()

    def stop_microphone(self):
        if self.microphone:
            self.microphone.close()
            self.microphone = None

    def grant_microphone_permission(self, page, url, feature):
        if feature == QWebEnginePage.Feature.MediaAudioCapture:
            page.setFeaturePermission(url, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)
        else:
            page.setFeaturePermission(url, feature, QWebEnginePage.PermissionPolicy.PermissionDeniedByUser)

    def handle_permission_request(self, origin, feature):
        if feature == QWebEnginePage.Feature.MediaAudioCapture:
            return True
        return False