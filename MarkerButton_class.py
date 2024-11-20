from lib import PWidget
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

button_color = '#D1D0D0'
background_color = "#b0bed1"

class MarkerButton(PWidget):
    """
    Button to send a marker string to the pupil companion app the will be stored in the phone recording.
    Then content of the marker strings can be edited in the UI
    """
    def __init__(self, num = 1):
        super().__init__()                                                   
        self.setStyleSheet(f'markerButton {{ background-color: {background_color}; border-radius: 8px }}')
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        
        self.send_button = QPushButton(QIcon("./assets/send.png"),"Send    ")
        self.send_button.setLayoutDirection(Qt.RightToLeft)
        self.send_button.pressed.connect(self.send_marker)
        self.send_button.setStyleSheet(f'background-color: {button_color}')
        self.send_button.released.connect(lambda: self.send_button.setStyleSheet(f'background-color: {button_color}'))
        self.send_button.setFixedHeight(40)                               
        self.layout.addWidget(self.send_button,50)
        
        self.name_line = QLineEdit(f"marker {num}")
        self.layout.addWidget(self.name_line,50)
        
    def send_marker(self):
        global pupil_dev 
        
        self.send_button.setStyleSheet('background-color: #64BACF')
        print(self.name_line.text()," sent")
        if pupil_dev:
            pupil_dev.send_event(self.name_line.text())
            print(self.name_line.text()," sent")