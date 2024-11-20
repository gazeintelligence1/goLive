from lib import PWidget

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QCheckBox

from PyQt5.QtGui import QPixmap

from PyQt5.QtCore import Qt

class Device_box(PWidget):
    """
    Box to display a connected device and its controls
    """
    def __init__(self, name : str, dev_type : str, sig):
        """
        Parameters
        ----------
        name : str
            name of the device to be displayed
        dev_type : str
            model of the device ("faros" or "pupil")
        """
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.setStyleSheet('background-color: #e6e6e6')
        self.setFixedHeight(70)
        
        dev_icon = QLabel()
        if dev_type == 'faros':
            dev_icon.setPixmap(QPixmap("./assets/icon-faros.png").scaled(60,60, transformMode =Qt.SmoothTransformation))
        if dev_type == 'pupil':
            dev_icon.setPixmap(QPixmap("./assets/icon-pupil.png").scaled(60,60, transformMode =Qt.SmoothTransformation))
        self.layout.addWidget(dev_icon,20)
        
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(name_label,80)
        
        if dev_type == 'faros':
            plot_button = QCheckBox('Show \n ECG')
            plot_button.stateChanged.connect(sig.showECG)
            self.layout.addWidget(plot_button,20)
        else:
            head_button = QCheckBox('Show \n head')
            head_button.stateChanged.connect(sig.show_head)
            self.layout.addWidget(head_button, 20)

    