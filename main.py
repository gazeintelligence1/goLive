from Signal_class import Signal
from MainWindow_class import MainWindow

from PyQt5.QtWidgets import QApplication
from multiprocessing import Process, Queue, freeze_support


if __name__ == "__main__" :

    # Objet : Assurer que le script continue de fonctionner correctement lorsqu'il est exécuté en tant qu'exécutable standalone.
    freeze_support()
    
    sig = Signal()

    pupil_dev, pupil_worker = None, None #slots for pupil neon device and workers, will be filled upon successful discovery
    recording = False

    app = QApplication([])
    
    QApplication.setStyle("fusion")

    win = MainWindow()
    
    win.set_instance(win)
    #sig.newDevice.connect(win.addDevice)