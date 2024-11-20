import threading
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QPushButton
from Separateur_class import Separateur
from LoadingAnimation_class import LoadingAnimation
from PupilIpBox_class import PupilIpBox
from Device_box_class import Device_box
import bluetooth
from PupilWorker_class import PupilWorker

import pupil_labs.realtime_api.simple as pupil

from faros import libfaros

button_color = '#D1D0D0'

class DeviceList(QWidget):
    """
    Displays the disovered devices and search related elements
    """
    n_devices = 0
    running_searches = ["faros","pupil"]
    found_devices = []
    
    def __init__(self, sig, MainWindow):
        super().__init__()
        self.sig = sig
        self.MainWindow = MainWindow
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(Separateur("Connected Devices"))
        self.layout.setContentsMargins(0,0,0,0)
        sig.doneSearching.connect(self.onDoneSearching)
        
        self.loading_animation = LoadingAnimation()
        self.layout.addWidget(self.loading_animation)
        
        self.retryButton = QPushButton("Retry search")
        self.retryButton.setStyleSheet(f'background-color: {button_color}')
        self.retryButton.clicked.connect(self.relaunchSearch(sig))
        self.retryButton.setFixedHeight(40)
        self.layout.addWidget(self.retryButton)
        self.retryButton.hide()
        
        self.pupil_ip_box = PupilIpBox()
        self.layout.addWidget(self.pupil_ip_box)
        self.pupil_ip_box.hide()
        
        self.layout.addStretch()
        
    def addDevice(self, name, dev_type):
        self.layout.insertWidget(1,Device_box(name,dev_type, self.sig, self.MainWindow))
        self.found_devices.append(dev_type)
        self.n_devices += 1
        
    def onDoneSearching(self,device_type : str):
        """
        Update the search UI to show that the search for a certain model is done
        
        Parameters
        ----------
        device_type : str
            model of the device ('faros' or 'pupil').

        """
        self.running_searches.remove(device_type)
        if len(self.running_searches) == 0:
            self.loading_animation.hide()
            if not ('faros' in self.found_devices and 'pupil' in self.found_devices):
                self.retryButton.show()
            if not 'pupil' in self.found_devices:
                self.pupil_ip_box.show()
            return
        
        l = self.loading_animation.text_label
        if device_type == 'faros':
            l.setText(l.text().replace('Faros','').replace(',',''))
        if device_type == 'pupil':
            l.setText(l.text().replace('Pupil','').replace(',',''))
    

    def find_faros(self, sig):
        """
        look for nearby faros devices on the bluetooth network and connect to the first on then start streaming 
        its data to the LSL
        """
        print("searching for faros device ..\n")
        try:
            bluetooth_devices = bluetooth.discover_devices(lookup_names=True)
            print(bluetooth_devices)
            faros_devices = [dev for dev in bluetooth_devices if 'FAROS' in dev[1]]
            print('Foud Faros:', faros_devices)
            
            if len(faros_devices) != 0:
                mac = faros_devices[0][0]   
                name = faros_devices[0][1]
                
                socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                socket.connect((mac, 5))
                
                res = libfaros.send_command(socket, "wbaoms", 7)
                
                properties  = libfaros.get_properties(socket)
                settings  = libfaros.unpack_settings(properties['settings'])   
                
                global streamer_thread
                streamer_thread = libfaros.stream_lsl(socket,settings, name)
                streamer_thread.start()
                sig.newDevice.emit(name, 'faros')
                print("done seraching faros")
        
        except Exception as e:
            print("Error in faros thread:",e)
            socket.close()
        finally:
            sig.doneSearching.emit("faros")     


    def setup_pupil_device(pupil_dev : pupil.Device, sig, win):
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
        
        pupil_worker.newFrame.connect(win.video_box.on_new_frame)
        pupil_worker.newGaze.connect(win.onNewGaze)
        pupil_worker.newAcc.connect(win.head_widget.onNewData)

        sig.newDevice.emit(pupil_dev.phone_name, 'pupil')

    def find_pupil(self, sig):
        """
        launch the discovery of a pupil neon device. first through the api's search function then by trying to 
        connect directly to neon.local:8080 if it fails
        """
        print("searching for pupil invisible device ..\n")
        global pupil_dev
        pupil_dev = pupil.discover_one_device()
        if pupil_dev == None:
            try:
                print("looking up neon.local")
                pupil_dev = pupil.Device(address='neon.local', port=8080)
            except Exception as e:
                print('error in pupil discovery thread:', e)
        if pupil_dev:
            print("found the following device:", pupil_dev)
            self.setup_pupil_device(pupil_dev, self.sig, self.MainWindow)
        else:
            print("no Pupil device found")
        sig.doneSearching.emit("pupil")

    def relaunchSearch(self, sig):
        if "faros" not in self.found_devices:
            self.running_searches.append("faros")
            threading.Thread(target=self.find_faros(sig)).start()          
            self.loading_animation.text_label.setText('Searching for \n Faros ..')
        if "pupil" not in self.found_devices:
            self.running_searches.append("pupil")
            threading.Thread(target=self.find_pupil(sig)).start()            
            self.loading_animation.text_label.setText('Searching for \n Pupil ..')
        if 'pupil' not in self.found_devices and 'faros' not in self.found_devices:
            self.loading_animation.text_label.setText('Searching for \n Pupil, Faros ..')
            
        self.retryButton.hide()
        self.pupil_ip_box.hide()
        self.loading_animation.show()

