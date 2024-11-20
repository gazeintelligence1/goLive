from lib import PWidget, Indicator, FixationIndicator, CustomRangeIndicator
from Separateur_class import Separateur

from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon

button_color = '#D1D0D0'

class IndicatorColumn(PWidget):
    
    def __init__(self, parent):
        super().__init__()
        
        self.setStyleSheet("background-color: white")
        self.layout = QVBoxLayout(self)
        
        close_button = QPushButton(icon = QIcon("./assets/close-icon.svg"))
        close_button.clicked.connect(parent.close)
        close_button.setFixedHeight(60)
        close_button.setStyleSheet(f'background-color: {button_color}')
        self.layout.addWidget(close_button)
        
        pupil_title = Separateur('Pupil')
        pupil_title.setMaximumHeight(80)
        self.layout.addWidget(pupil_title)
        
        self.battery_indicator = Indicator("assets/icon-battery.png","Battery")
        self.layout.addWidget(self.battery_indicator)
        
        self.storage_indicator = Indicator("assets/icon-storage.png","Storage")
        self.layout.addWidget(self.storage_indicator)
        
        self.fixation_counter = FixationIndicator("assets/icon-fixation.png", "Fixations")
        
        self.layout.addWidget(self.fixation_counter)
        self.layout.addStretch(10)
        
        faros_title = Separateur('Faros ECG')
        self.layout.addWidget(faros_title)
        
        self.hr_indicator = Indicator("assets/icon-HR.png","BPM")
        self.layout.addWidget(self.hr_indicator)
        
        self.hrv_indicator = CustomRangeIndicator("assets/icon-HRV.png", "HRV (sdnn)",unit='ms')
        self.layout.addWidget(self.hrv_indicator)
        
        self.acc_indicator = CustomRangeIndicator("assets/icon-activity.png", "Activity level")
        self.layout.addWidget(self.acc_indicator)
        
        self.layout.addStretch(10)