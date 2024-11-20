
from lib import PWidget
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QCheckBox, QSlider, QDesktopWidget
from MarkerBox_class import MarkerBox
from PyQt5.QtGui import QPixmap
from DeviceList_class import DeviceList
from PyQt5.QtCore import Qt

import numpy as np
import mss
import cv2
import time
import datetime
from multiprocessing import Process, Event

button_color = '#D1D0D0'

def record_screen(stop_event, output_filename="output.avi", frame_rate=12, width=1920, height=1080):
    """

    Parameters
    ----------
    stop_event : multiprocessing.Event
        signal to inform the process that the "record screen" checkbox has been unchecked
    output_filename : str, optional
        name of the video file. The default is "output.avi".
    frame_rate : int, optional
        The default of 12 has been chosen because it correspond to the max frame that the function can write per seconds on the current hardware.
        Any higher frameratethat that and the video will be sped up.
        
    width : int, optional
        Width of the captured area. The default is 1920.
    height : int, optional
        Height of the captured area. The default is 1080.


    """
    try:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter("recordings/" + output_filename, fourcc, frame_rate, (width, height))
        print("issou")
        with mss.mss() as sct:
            monitor = {"top": 0, "left": 0, "width": width , "height": height }
    
            while not stop_event.is_set():
                
                img = np.array(sct.grab(monitor))
                out.write(cv2.cvtColor(img, cv2.COLOR_BGRA2BGR))
                
                
    except Exception as e:
        print("Error in recording process:", e)
    finally:
        out.release()


class ControlPanel(PWidget):
    def __init__(self, sig):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("background-color: white")
        self.layout.setContentsMargins(10,5,10,0)
        
        self.logo = QLabel()
        self.logo.setFixedHeight(80)
        self.logo.setPixmap(QPixmap("./assets/logo.png").scaled(300,45, transformMode=Qt.SmoothTransformation))
        self.layout.addWidget(self.logo, stretch = 3)
        
        self.layout.addStretch(1)

        self.start_button = QPushButton("Start Recording")
        self.start_button.setFixedHeight(60)
        self.start_button.clicked.connect(self.start_recording)
        self.start_button.setStyleSheet(f'background-color: {button_color}')
        self.start_button.setDisabled(True)
        self.layout.addWidget(self.start_button, stretch = 2)
        
        self.marker_box = MarkerBox()
        self.layout.addWidget(self.marker_box, stretch = 5)
        
        self.device_list = DeviceList(sig)
        self.layout.addWidget(self.device_list, stretch = 5)
        
        options_box = QVBoxLayout()
        
        self.recording_checkbox = QCheckBox("screen recording")
        self.recording_checkbox.clicked.connect(self.record_screen)
        self.recording_checkbox.setStyleSheet("margin-top: 8px; margin-bottom: 8px")
        options_box.addWidget(self.recording_checkbox)
        
        options_box.addWidget(QLabel("Circle size :"))
        self.circle_size_slider = QSlider(Qt.Horizontal)
        options_box.addWidget(self.circle_size_slider)
        self.circle_size_slider.setMaximum(100)
        self.circle_size_slider.setMinimum(0)
        self.circle_size_slider.setValue(50)
        
        self.layout.addLayout(options_box)
        
        self.layout.addStretch(1)
    def start_recording(self):
        """
        start the recording in the pupil neon companion app
        """
        global pupil_dev
        if pupil_dev is not None:
            try:
                pupil_dev.recording_start()
            except:
                print("device was already recording")
            self.start_button.clicked.connect(self.stop_recording)
            self.start_button.clicked.disconnect(self.start_recording)
            self.start_button.setText("Stop Recording")
            
    def stop_recording(self):
        """
        stop the recording in the pupil neon companion app
        """
        global pupil_dev
        if pupil_dev is not None:
            try:
                pupil_dev.recording_stop_and_save()
            except:
                print("device wasnt recording")
            self.start_button.clicked.connect(self.start_recording)
            self.start_button.clicked.disconnect(self.stop_recording)
            self.start_button.setText("Start recording")
        
    def enable_button_after(self, delay=1.5):
        time.sleep(delay)
        self.start_button.setEnabled(True)
        
    def record_screen(self, state):
        '''
        start or stop the recording of the app's screen 

        Parameters
        ----------
        state : int
            Status of 'record screen' checkbox. 2(checked) or 0(unchecked)

        '''
        if state == True:
            screen_size = QDesktopWidget().screenGeometry(-1)
            width, height = screen_size.width() * 2, screen_size.height() * 2
            filename = datetime.datetime.now().strftime('%d-%m-%y %Hh%Mm%Ss') + ".avi"
            
            self.stop_event = Event()
            self.recording_process = Process(target=record_screen, kwargs={"stop_event":self.stop_event,
                                                                           "width" : width,
                                                                           "height" : height,
                                                                           "output_filename" : filename})
            self.recording_process.start()

        if state == False:
            if not hasattr(self,"stop_event"):
                return
            
            if self.stop_event:
                self.stop_event.set()

            if self.recording_process:
                self.recording_process.join()