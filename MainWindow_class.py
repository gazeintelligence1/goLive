import time as time
import threading
import pylsl as lsl
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QHBoxLayout

from lib import PWidget, get_hrv
from IndicatorColumn_class import IndicatorColumn
from VideoBox_class import VideoBox
from ControlPanel_class import ControlPanel
from HeadIndicator_class import HeadIndicator
from FarosWorker_class import FarosWorker

class MainWindow(PWidget):
    """
    Classe principale qui configure l'interface utilisateur de l'application.
    """
    # Variables de classe qui sont partagées entre toutes les instances de la classe, car elles ne sont pas définies avec self
    rr_intervals = []
    hrv_interval = None
    acc_diffs = np.array([])
    
    last_gaze = None
    time_fixating = 0
    in_fixation = False
    fixations = []
    
    # Constructeur
    def __init__(self):
        super().__init__() # Appel du constructeur de la classe parent PWidget
        global main_win # Déclaration d'une variable globale pour référencer l'instance actuelle de MainWindow
        main_win = self # Affectation de l'instance actuelle à la variable globale

        #  Style de la fenêtre
        border_color = '#95accc' # Couleur de fond
        self.setStyleSheet(f"font-size:15px; font-weight:550; background-color:{border_color}") # Applique un style CSS
        self.setWindowTitle("GoLive") # Titre de la fenêtre

        # Création et configuration du layout principal en grille (QGridLayout)
        self.layout = QGridLayout(self) # Création d'un layout en grille pour la fenêtre principale
        self.layout.setContentsMargins(0,0,0,0)
        
        self.indicator_column = IndicatorColumn(self)
        self.layout.addWidget(self.indicator_column, 0, 0, 2, 1)
        self.layout.setColumnStretch(0, 12)

        self.video_box = VideoBox()
        self.layout.addWidget(self.video_box, 0, 1, 1, 2)
        self.layout.setColumnStretch(1, 55)
        self.layout.setColumnStretch(2, 30)
        self.layout.setRowStretch(0, 80)

        self.control_panel = ControlPanel()
        self.layout.addWidget(self.control_panel, 0, 3, 2, 1)
        self.layout.setColumnStretch(3, 5)
        
        #those are here to test the UI without having to connect the devices.
        #self.addDevice('Faros-253TEST', 'faros')
        #self.addDevice('OnePlus 11TEST','pupil')
        
        self.extras_layout = QHBoxLayout()
        

        self.ecg_plot = pg.GraphicsLayoutWidget(self)
        self.ecg_plot.setBackground('w')
        self.ecg_plot.window = self.ecg_plot.addPlot()
        self.ecg_plot.window.showGrid(x=True, y=True, alpha=0.5)
        self.ecg_plot.hide()
        self.ecg_curve = pg.PlotCurveItem(pen="b")
        self.ecg_plot.window.addItem(self.ecg_curve)
        
        self.extras_layout.addWidget(self.ecg_plot,65)
        

        self.head_widget = HeadIndicator()
        self.head_widget.setStyleSheet('background-color : black')
        self.head_widget.hide()
        
        self.extras_layout.addWidget(self.head_widget,35)
        
        self.layout.addLayout(self.extras_layout, 1, 1, 1, 2)
        
    def addDevice(self, name : str, dev_type : str):
        """
        Parameters
        ----------
        name : str
            name of the specific device (ex: FAROS-299055).
        dev_type : str
            model of the device, is either 'faros' or 'pupil'.
        """

        self.control_panel.device_list.addDevice(name, dev_type)
        print(f"adding device {name} of type {dev_type}")
        if dev_type == "faros":
            self.faros_worker = FarosWorker(name)
            self.faros_thread = threading.Thread(target = self.faros_worker.receiveFaros)
            self.faros_thread.start()
            print("faros thread started")
            
        if dev_type == "pupil":
            self.control_panel.start_button.setDisabled(False)
            threading.Thread(target= self.update_PI_state).start()
            
    def showECG(self, win, state : int):
        """
    
        Parameters
        ----------
        state : int
            state if the "show ecg" checkbox, either 2 (checked) or 0 (unchecked).

        """
        print("showing ECG ... ")
        if state == 2:
            self.layout.setRowStretch(1, 26)
            self.ecg_plot.show()
            self.start_time = lsl.local_clock()
            self.ecg_curve.setData([], [])
            threading.Thread(target=self.scroll_plot(self.win)).start()
        if state == 0:
            self.ecg_plot.hide()
            if not self.head_widget.isVisible():
                self.layout.setRowStretch(1, 0)
            
    def show_head(self,state):
        if state == 2:
            self.head_widget.show()
            self.layout.setRowStretch(1, 26)
        if state == 0:
            self.head_widget.hide()
            if not self.ecg_plot.isVisible():
                self.layout.setRowStretch(1, 0)
                self.layout.setRowStretch(1, 0)
    
    def onNewGaze(self,gaze):
        if self.last_gaze:
            if abs(self.last_gaze.x - gaze.x) + abs(self.last_gaze.y - gaze.y) < self.indicator_column.fixation_counter.space_treshold:
                self.time_fixating +=  gaze.timestamp_unix_seconds - self.last_gaze.timestamp_unix_seconds 
            else:
                self.time_fixating = 0
                self.in_fixation = False
            
            treshold = self.indicator_column.fixation_counter.treshold / 1000
            if self.time_fixating >= treshold: #250ms to consider a fixation
                if not self.in_fixation:
                    self.fixations.append(gaze)
                    self.in_fixation = True
                    
            n_fixations = len(self.fixations)
            self.indicator_column.fixation_counter.setValue(n_fixations)  
        self.last_gaze = gaze
            
    def onNewECG(self, timestamps, chunk):
        if self.ecg_plot.isVisible() and len(chunk) != 0:
            chunk = np.array(chunk)[:,0]
            self.ecg_curve.setData( np.append(self.ecg_curve.getData()[0],np.array(timestamps)-self.start_time)[-10000:], 
                                              np.append(self.ecg_curve.getData()[1], chunk )[-10000:] )
            
    def onNewRR(self, chunk):
        if len(chunk) != 0:
            rr = chunk[0][0] + 32768 #rr are sent with an offset of -32768 milliseconds so this is needed to get the value
            self.rr_intervals.append(rr)
            bpm = int(1/rr * 1000 * 60)
            self.indicator_column.hr_indicator.label.setText(f'{bpm}\nBPM')
            time_window = int(self.indicator_column.hrv_indicator.time_range)
            hrv = get_hrv(self.rr_intervals[-time_window:]) if time_window !=0 else get_hrv(self.rr_intervals)
            if hrv:
                self.indicator_column.hrv_indicator.label.setText(f"{hrv}ms\nHRV")
    
    def onNewAcc(self,chunk):
        chunk = np.array(chunk)
        acc_diff = np.abs(chunk[:-1,:] - chunk[1:,:])
        self.acc_diffs = np.append(self.acc_diffs, acc_diff)
        time_window = int(self.indicator_column.acc_indicator.time_range * self.acc_sr)
        
        mean_acc = np.mean(self.acc_diffs[-time_window:]) if time_window !=0 else np.mean(self.acc_diffs)
        mean_acc = max(mean_acc-9,0)    #!!! did -9 because mean_acc rarely gets below 9 even when still
        if mean_acc != None:
            self.indicator_column.acc_indicator.label.setText(f"{round(mean_acc,1)}\nActivity level") 
            
    def scroll_plot(self):
        """
        autoscrolls the ECG plot
        """
        print("start scrolling")
        while self.win.ecg_plot.isVisible():
            lsl_time = lsl.local_clock()
            self.ecg_plot.window.setXRange(lsl_time - 8 - self.start_time, lsl_time + 2 - self.start_time )
            time.sleep(0.08)
            self.ecg_plot.update()
            
    def update_PI_state(self):
        """
        periodically update the battery percentage and storage space of the pupil companion phone 
        """
        global pupil_dev

        while pupil_dev:
            self.indicator_column.battery_indicator.label.setText(f"{pupil_dev.battery_level_percent}%\nBattery")
            self.indicator_column.storage_indicator.label.setText(f"{pupil_dev.memory_num_free_bytes / 1024**3:.1f} GB\nStorage")
            time.sleep(5)

    def set_instance(self, win):
        self.win = win