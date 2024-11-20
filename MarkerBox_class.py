from lib import PWidget
from MarkerButton_class import MarkerButton
from PyQt5.QtWidgets import QVBoxLayout, QGridLayout
from Separateur_class import Separateur

class MarkerBox(PWidget):
    """
    Holds the pupil neon markers buttons
    """
    n_buttons = 0
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.layout.addWidget(Separateur("Send Events"))
        
        self.grid = QGridLayout()      
        for i in range(1,7):
            self.add_button()
        self.layout.addLayout(self.grid)  
        
    def add_button(self):
        self.grid.addWidget(MarkerButton(self.n_buttons +1), self.n_buttons//2, self.n_buttons % 2)
        self.n_buttons += 1
        button_size = 70                                                                                                                                                
        
        self.setMinimumHeight(((self.n_buttons // 2) + 1 )*button_size + 80)