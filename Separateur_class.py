from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QWidget

title_style = 'font-size: 18px; font-weight: 550; font-family: "Helvetica"'

class Separateur(QWidget):
    """
    Title and horizontal separator line to separate the blocks of Faros and Pupil indicator in the sidebar
    """
    def __init__(self, title):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setMaximumHeight(50)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignHCenter)
        title_label.setStyleSheet(title_style)
        self.layout.addWidget(title_label)
        
        splitLine = QFrame()
        splitLine.setFrameShape(QFrame.HLine)
        splitLine.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(splitLine)
        self.layout.addStretch(1)