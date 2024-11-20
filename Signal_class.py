from PyQt5.QtCore import QObject, pyqtSignal

"""
La classe Signal hérite de la classe QObject
"""

class Signal(QObject):
    """
    A class to pass signals globally

    Attributes
    ----------
    newDevice : pyqtSignal
        Signal emitted when a new device is detected. 
        It passes an int (device ID) and a str (device name).
        
    doneSearching : pyqtSignal
        Signal emitted when the search process for faros or pupil devices is done, wheter its sucessfull or not. 
        It passes a str that is the model of the device that's done being searched ('faros' or 'pupil').
    """
    
    newDevice = pyqtSignal(str, str) # signal pour un nouvel appareil
    doneSearching = pyqtSignal(str) # signal pour la fin de la recherche
