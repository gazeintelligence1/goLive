from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy, QPushButton, QLineEdit
from lib import is_valid_ip
import pupil_labs.realtime_api.simple as pupil
from PupilWorker_class import PupilWorker

button_color = '#D1D0D0'

class PupilIpBox(QWidget):
    """
    As a last recourse when all other method of connection to the puil neon glasses fail it is
    possible to enter the ip of the phone directly to avoid DNS issues. This is a widget that appear when the search fails
    and prompt the user to enter the ip of the companion phone then try to connect trough it
    """
    lookup_ip = pyqtSignal()
    def __init__(self, sig):
        super().__init__()
        self.sig = sig
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        
        l = QLabel("Can't find your Pupil device ? Try entering the ip displayed inside the companion app")
        l.setWordWrap(True)
        l.setStyleSheet("font-size: 12px; font-weight: 300")
        self.layout.addWidget(l)
        
        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        self.ip_field = QLineEdit()
        self.ip_field.setPlaceholderText("enter ip without the port (:8080)")
        self.ip_field.setStyleSheet("font-size: 12px ; font-weight: 200")
        hbox.addWidget(self.ip_field)
        
        self.confirm_button = QPushButton(" add ")
        self.confirm_button.clicked.connect(self.add_pupil_by_ip)
        self.confirm_button.setStyleSheet(f'background-color: {button_color}')
        self.confirm_button.pressed.connect(lambda: self.confirm_button.setStyleSheet('background-color: #64BACF'))
        self.confirm_button.released.connect(lambda: self.confirm_button.setStyleSheet(f'background-color: {button_color}'))
        hbox.addWidget(self.confirm_button)
        
        self.layout.addLayout(hbox)
        

    def setup_pupil_device(self, pupil_dev : pupil.Device):
        """
        launch the streams for a pupil neon device and connect them to the main window
        
        Parameters
        ----------
        pupil_dev : pupil.Device
            discovered pupil device from the pupil api

        """
        print("Setup pupil device:", pupil_dev)
        global pupil_worker
        pupil_worker = PupilWorker(pupil_dev)
        
        pupil_worker.newFrame.connect(self.sig.video_box.on_new_frame)
        pupil_worker.newGaze.connect(self.sig.onNewGaze)
        pupil_worker.newAcc.connect(self.sig.head_widget.onNewData)

        self.sig.newDevice.emit(pupil_dev.phone_name, 'pupil')


    def add_pupil_by_ip(self):
        ip = self.ip_field.text()
        if not is_valid_ip(ip):
            self.ip_field.setText("")
            self.ip_field.setPlaceholderText("error: this is not a valid ip (ex: 192.168.0.1)")
            return
    
        self.ip_field.setText('')
        self.ip_field.setPlaceholderText("trying to connect ...")
        try:
            pupil_dev = pupil.Device(address = ip,port='8080')
        except Exception as e:
            print(e)
            self.ip_field.setText('')
            self.ip_field.setPlaceholderText("error: can't find device with this ip")
            pupil_dev = None
        if pupil_dev:
            self.setup_pupil_device(pupil_dev)