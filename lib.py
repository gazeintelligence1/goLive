# -*- coding: utf-8 -*-
import math
import numpy as np

from PyQt5.QtWidgets import QWidget, QStyleOption, QStyle, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class PWidget(QWidget):
    """
    QWidget modifié pour permettre le changement de la couleur d'arrière-plan via un événement paintEvent personnalisé.
    Normal QWidgets can't have their background color modified so this is a QWidget with an overriden paintEvent to allow it
    """
    def __init__(self):
        super().__init__() # Appel du constructeur de la classe parent QWidget
    
    # Surchargée pour permettre le dessin personnalisé de l'arrière-plan. Elle utilise QPainter et QStyle pour dessiner le widget.
    def paintEvent(self, event): 
        opt = QStyleOption() # Création d'une option de style pour configurer le widget
        opt.initFrom(self) # Initialisation des paramètres du style
        painter = QPainter(self) # Création d'un objet QPainter pour dessiner sur le widget
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self) # Dessin du widget avec le style personnalisé

class Indicator(QWidget):
    """
    Visual indicator to display a numeric value with an icon
    """
    def __init__(self, icon_link : str, title : str ,unit = ''):
        super().__init__()
        self.title, self.unit = title, unit
        self.setStyleSheet("background-color: #b0bed1 ")
        self.layout = QVBoxLayout(self)
        
        icon = QLabel()
        icon.setAlignment(Qt.AlignCenter)       
        icon.setPixmap(QPixmap(QPixmap("./"+icon_link).scaledToHeight(30)))
        self.layout.addWidget(icon)
        
        self.label = QLabel(f"--{unit}\n{title}")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet('font-size: 15px')
        self.layout.addWidget(self.label)
        
    def setValue(self, value):
        self.value = value
        self.label.setText(f'{value}{self.unit}\n{self.title}')


        

class CustomRangeIndicator(Indicator):
    time_range = 0
    """
    Indicator with an input to modify the timeframe of the measurements
    """
    def __init__(self, icon_link,title,unit = ''):
        super().__init__(icon_link = icon_link,title = title, unit = unit)
        
        interval_control_box = QHBoxLayout()
        self.layout.addLayout(interval_control_box)
        
        l = QLabel("Interval:")
        l.setStyleSheet("font-size: 15px")
        interval_control_box.addWidget(l)
        
        interval_spinbox = QSpinBox()
        interval_spinbox.setMinimumHeight(30)
        interval_spinbox.setRange(0, 9999)
        interval_spinbox.setSingleStep(10)
        interval_spinbox.setSuffix("s")
        interval_spinbox.setSpecialValueText('∞')
        interval_spinbox.setStyleSheet('background-color: white; font-size: 14px; font-weight: 500;')
        interval_spinbox.valueChanged.connect(self.update_range)
        interval_spinbox.setValue(10)
        interval_control_box.addWidget(interval_spinbox)
        
        self.interval_spinbox = interval_spinbox
        
    def update_range(self,value):
        """
        Parameters
        ----------
        value : int
            the timeframe on which the measurements is to be made. Purely indicative, other parts of the programm read
            it to implement the measurement.
        """
        self.time_range = value

        
class FixationIndicator(Indicator):
    treshold = 0
    space_treshold = 0
    """
    A custom made indicator to display the number of fixations from the eyetracker 
    """
    def __init__(self, icon_link,title,unit = ''):
        super().__init__(icon_link = icon_link,title = title, unit = unit)
        
        interval_control_box = QHBoxLayout()
        self.layout.addLayout(interval_control_box)
        
        #workaround to a bug where, when video and ecg graph are showing, after a minute or so the video and graph freeze
        #until any button is pressed somewhere in the app. App cant freeze if you press a button every 0.5s >:) 
        l = QPushButton("Duration:")
        l.setStyleSheet("border: none; font-size: 13px; text-align: left")
        l.clicked.connect(lambda: int())
        self.debug_timer = QTimer()
        self.debug_timer.timeout.connect(lambda: l.animateClick())
        self.debug_timer.start(500)
        interval_control_box.addWidget(l)
        #..
        interval_spinbox = QSpinBox()
        interval_spinbox.setMinimumHeight(30)
        interval_spinbox.setMinimumWidth(65)
        interval_spinbox.setRange(0, 9999)
        interval_spinbox.setSingleStep(10)
        interval_spinbox.setSuffix("ms")
        interval_spinbox.setStyleSheet('background-color: white; font-size: 13px; font-weight: 500;')
        interval_spinbox.valueChanged.connect(self.update_treshold)
        interval_spinbox.setValue(250)
        self.interval_spinbox = interval_spinbox
        interval_control_box.addWidget(interval_spinbox)
        
        
        space_control_box = QHBoxLayout()
        l2 = QLabel("Dispersion:")
        l2.setStyleSheet("font-size: 13px; text-align: left")
        space_control_box.addWidget(l2)
        
        self.space_treshold_spinbox = QSpinBox()
        self.space_treshold_spinbox.setMinimumHeight(30)
        self.space_treshold_spinbox.setMinimumWidth(65)
        self.space_treshold_spinbox.setRange(10, 200)
        self.space_treshold_spinbox.setSingleStep(5)
        self.space_treshold_spinbox.setSuffix("px")
        self.space_treshold_spinbox.setStyleSheet('background-color: white; font-size: 14px; font-weight: 500;')
        self.space_treshold_spinbox.valueChanged.connect(self.update_space_treshold)
        self.space_treshold_spinbox.setValue(50)
        space_control_box.addWidget(self.space_treshold_spinbox)
        
        self.layout.addLayout(space_control_box)
        
        
    def update_treshold(self,value):
        """
        update the minimum time treshold to consider detect a fixations. Indicative, other functions read from it to detect a fixation
        Parameters
        ----------
        value : int
            minimum duration of a fixation in milliseconds.
        """
        self.treshold = value
        
    def update_space_treshold(self, value):
        """
        update the maximum dispertion needed to break a fixation. Indicative, other functions read from it to detect a fixation
        Parameters
        ----------
        value : int
            maximum dispertion needed to break a fixation (in pixels).
        """
        self.space_treshold = value

def get_hrv(intervals: list):
    """
    calculate HRV from RR intervals
    
    Parameters
    ----------
    intervals : list
        a list of consecutive RR intervals.

    Returns
    -------
    float
        the HRV for the given intervals

    """
    if not intervals:
        print("no rr intervals in timeframe, cant calculate hrv")
        return
    intervals = [x for x in intervals if x < 4000 and x > 250] #filter heart rate below 30bpm or over 240bpm
    return round(np.std(intervals),2)

def is_valid_ip(ip):
    nums = ip.split('.')
    if len(nums) == 4:
        try:
            for num in nums:
                if int(num) < 0 or int(num) > 255:
                    return False          
        except:
            return False
        return True

        