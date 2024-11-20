import threading
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QPushButton
from Separateur_class import Separateur
from LoadingAnimation_class import LoadingAnimation
from PupilIpBox_class import PupilIpBox
from Device_box_class import Device_box
import bluetooth

from faros import libfaros

button_color = '#D1D0D0'

class DeviceList(QWidget):
    """
    Displays the disovered devices and search related elements
    """
    n_devices = 0
    running_searches = ["faros","pupil"]
    found_devices = []
    
    def __init__(self, sig):
        super().__init__()
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
        self.layout.insertWidget(1,Device_box(name,dev_type))
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
    

    def find_faros(sig):
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

