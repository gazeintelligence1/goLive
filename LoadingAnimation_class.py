from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QSize

class LoadingAnimation(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        gif = QMovie("./assets/loading.gif")
        gif.setScaledSize(QSize(46,46))
        self.gif_label.setMovie(gif)
        gif.start()     
        self.layout.addWidget(self.gif_label) 
        
        self.text_label = QLabel('Searching for Pupil, Faros ..')
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("color : grey")
        self.layout.addWidget(self.text_label)