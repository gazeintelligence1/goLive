import pylsl as lsl
from PyQt5.QtCore import QObject, pyqtSignal
import time

class FarosWorker(QObject):
    """
    worker thread to receive and transmit data from the lsl stream of the current Faros device
    
    Attributes
    ----------
    newECG : pyqtSignal
        Signal emitted when a new ECG data is received from the lsl stream of the Faros
        
    newGaze : pyqtSignal
        Signal emitted when new RR intervals are received from the lsl stream of the Faros
        
    newAcc : pyqtSignal
        Signal emitted when new accelerometer data are received from the lsl stream of the Faros
    """
    sampling = True
    newECG = pyqtSignal(object, object)
    newRR = pyqtSignal(object)
    newAcc = pyqtSignal(object)
    
    def __init__(self, faros_name : str, win):
        """
        Parameters
        ----------
        faros_name : str
            Name of the specific faros device, used to match the correct lsl stream.
        """
        super().__init__()
        self.faros_name = faros_name
    
    def receiveFaros(self, win):
        """
        resolve the lsl streams corresponding the specified faros then sample them periodicaly and transmit the data.
        """
        ecg_streams = lsl.resolve_byprop('name',self.faros_name+'_ECG',timeout=1)
        rr_streams = lsl.resolve_byprop('name', self.faros_name+'_RR',timeout=1)
        acc_streams = lsl.resolve_byprop('name', self.faros_name+'_acc',timeout=1)
        
        
        self.newECG.connect(win.onNewECG)
        self.newRR.connect(win.onNewRR)
        self.newAcc.connect(win.onNewAcc)
        
        ecg_inlet, rr_inlet, acc_inlet = None, None, None
        if len(ecg_streams) != 0:
            ecg_inlet = lsl.StreamInlet(ecg_streams[0])
            win.ecg_sr = ecg_inlet.info().nominal_srate()
        if len(rr_streams) != 0:
            rr_inlet = lsl.StreamInlet(rr_streams[0])   
        if len(acc_streams) != 0:
            acc_inlet = lsl.StreamInlet(acc_streams[0])  
            win.acc_sr = acc_inlet.info().nominal_srate()
        
        print(ecg_inlet, rr_inlet, acc_inlet)
        while self.sampling:
            if ecg_inlet:
                ecg_data, ecg_ts = ecg_inlet.pull_chunk()
                self.newECG.emit(ecg_ts, ecg_data)
            if rr_inlet:
                rr_data, rr_ts = rr_inlet.pull_chunk()
                self.newRR.emit(rr_data)
            if acc_inlet:
                acc_data, acc_ts = acc_inlet.pull_chunk()
                if acc_ts:
                    self.newAcc.emit(acc_data)
            time.sleep(0.1)
        
    def stop(self):
        self.sampling = False
        