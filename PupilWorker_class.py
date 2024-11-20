from PyQt5.QtCore import pyqtSignal, QObject
import threading
import time

class PupilWorker(QObject):
    """
    worker thread to receive and transmit data from the pupil device trough.
    
    Attributes
    ----------
    newFrame : pyqtSignal
        Signal emitted when a new video frame from the scene camera is received
        
    newGaze : pyqtSignal
        Signal emitted when a new gaze data point is received. Is always matched to a frame in this configuration
        
    newAcc : pyqtSignal
        Signal emitted when new accelerometer data are received.
    """
    
    sampling = True
    newFrame = pyqtSignal(object, object)
    newGaze = pyqtSignal(object)
    newAcc = pyqtSignal(object, object)

    def __init__(self, pupil_dev):
        super().__init__()
        self.dev = pupil_dev
        threading.Thread(target=self.receiveFrames).start()
        threading.Thread(target=self.receive_acc).start()

    def receiveFrames(self):
        """
        wait for new frames and gaze data and publishes them
        """
        i = 1
        start_time = None
        while self.sampling:
            frame, gaze = self.dev.receive_matched_scene_video_frame_and_gaze()
            if not start_time:
                start_time = time.time()
                
            self.newFrame.emit(frame, gaze)
            self.newGaze.emit(gaze)
            i += 1
    
    def receive_acc(self):
        """
        wait for new accelerometer data and publishes it
        """
        while self.sampling:
            acc_data = self.dev.receive_imu_datum()
            chunk = {
                "acc_x": (acc_data.accel_data.x, ),
                "acc_y": (acc_data.accel_data.y, ),
                "acc_z": (acc_data.accel_data.z, ),
                "gyro_x": (acc_data.gyro_data.x, ),
                "gyro_y": (acc_data.gyro_data.y, ),
                "gyro_z": (acc_data.gyro_data.z, ),
                "quaternion_x": (acc_data.quaternion.x, ),
                "quaternion_y": (acc_data.quaternion.y, ),
                "quaternion_z": (acc_data.quaternion.z, ),
                "quaternion_w": (acc_data.quaternion.w, )
            }

            self.newAcc.emit([acc_data.timestamp_unix_seconds], chunk)

    def stop(self):
        self.sampling = False