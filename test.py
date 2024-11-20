from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QHBoxLayout, QStyle, QStyleOption, QDesktopWidget
from PyQt5.QtGui import QPainter
import pyqtgraph as pg
import numpy as np
import threading
from FarosWorker_class import FarosWorker
from ControlPanel_class import ControlPanel
import sys
from multiprocessing import freeze_support
from Signal_class import Signal

# Classe PWidget qui hérite de QWidget, utilisée pour permettre la personnalisation du fond
class PWidget(QWidget):
    """
    QWidget modifié pour permettre le changement de la couleur d'arrière-plan via un événement paintEvent personnalisé.
    """
    def __init__(self):
        super().__init__()  # Appel du constructeur de la classe parent QWidget

    def paintEvent(self, event):
        """Surchargée pour dessiner un arrière-plan personnalisé."""
        opt = QStyleOption()  # Création d'une option de style pour configurer le widget
        opt.initFrom(self)  # Initialisation des paramètres du style
        painter = QPainter(self)  # Création d'un objet QPainter pour dessiner sur le widget
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)  # Dessin du widget avec le style personnalisé

# Classe MainWindow qui hérite de PWidget pour construire l'interface principale
class MainWindow(PWidget):
    
    # Variables de classe qui sont partagées entre toutes les instances de la classe, car elles ne sont pas définies avec self
    rr_intervals = []
    hrv_interval = None
    acc_diffs = np.array([])
    
    last_gaze = None
    time_fixating = 0
    in_fixation = False
    fixations = []
    
    """
    Classe principale qui configure l'interface utilisateur de l'application.
    """
    def __init__(self):
        super().__init__()  # Appel du constructeur de la classe parent PWidget

        global main_win  # Déclaration d'une variable globale pour référencer l'instance actuelle de MainWindow
        main_win = self  # Affectation de l'instance actuelle à la variable globale

        # Configuration du style et du titre de la fenêtre
        border_color = '#95accc'  # Définition de la couleur de fond
        self.setStyleSheet(f"font-size:15px; font-weight:550; background-color:{border_color}")
        self.setWindowTitle("GoLive")  # Titre de la fenêtre

        # Get the screen size
        # screen = QDesktopWidget().screenGeometry()  # Get screen geometry
        # screen_width = screen.width()
        # screen_height = screen.height()

        # # Calculate margins as a percentage of screen size
        # left_margin = 0  # 5% of screen width
        # top_margin = 0 # 5% of screen height
        # right_margin = int(screen_width)  # 5% of screen width
        # bottom_margin = int(screen_height * 0.9)  # 5% of screen height

        # Création du layout (mise en page) principal en grille
        #self.layout = QGridLayout(self)  # Création d'un layout en grille pour la fenêtre principale        
        #self.layout.setContentsMargins(left_margin, top_margin, right_margin, bottom_margin) # Set the margins dynamically

        self.layout = QGridLayout(self) # Création d'un layout en grille pour la fenêtre principale
        self.layout.setContentsMargins(0,0,0,0)
        
        #self.layout.setContentsMargins(500, 250, 500, 500)  # Marges à zéro pour le layout (tailler fenêtre)

        # Ajout de l'indicateur (widget simulé ici)
        self.indicator_column = QWidget(self)  # Remplacer QWidget par la classe réelle IndicatorColumn
        self.layout.addWidget(self.indicator_column, 0, 0, 2, 1)  # Placement du widget dans la grille
        self.layout.setColumnStretch(0, 12)  # Ajustement de l'espace de la colonne

        # Ajout de la boîte vidéo (widget simulé ici)
        self.video_box = QWidget(self)  # Remplacer QWidget par la classe réelle VideoBox
        self.layout.addWidget(self.video_box, 0, 1, 1, 2)  # Placement du widget dans la grille
        self.layout.setColumnStretch(1, 55)  # Ajustement de l'espace des colonnes
        self.layout.setColumnStretch(2, 30)
        self.layout.setRowStretch(0, 80)  # Ajustement de l'espace de la ligne

        # # # Ajout du panneau de contrôle (widget simulé ici)
        self.control_panel = ControlPanel(sig, MainWindow)  # Remplacer QWidget par la classe réelle ControlPanel
        self.layout.addWidget(self.control_panel, 0, 3, 2, 1)
        self.layout.setColumnStretch(3, 5)

        self.addDevice('Faros-253TEST', 'faros')
        self.addDevice('OnePlus 11TEST','pupil')

        # # Création d'un layout supplémentaire pour d'autres widgets
        # self.extras_layout = QHBoxLayout()

        # # # Ajout du widget de graphique ECG (utilisant pyqtgraph)
        # self.ecg_plot = pg.GraphicsLayoutWidget(self)
        # self.ecg_plot.setBackground('w')  # Fond blanc pour le graphique
        # self.ecg_plot.window = self.ecg_plot.addPlot()  # Ajout d'une fenêtre de tracé
        # self.ecg_plot.window.showGrid(x=True, y=True, alpha=0.5)  # Affichage de la grille
        # self.ecg_plot.hide()  # Masquage initial du widget
        # self.ecg_curve = pg.PlotCurveItem(pen="b")  # Courbe bleue pour l'ECG
        # self.ecg_plot.window.addItem(self.ecg_curve)  # Ajout de la courbe à la fenêtre

        # # # Ajout du widget ECG au layout des extras
        # self.extras_layout.addWidget(self.ecg_plot, 65)

        # # # Ajout d'un widget indicateur de tête (widget simulé ici)
        # self.head_widget = QWidget(self)  # Remplacer QWidget par la classe réelle HeadIndicator
        # self.head_widget.setStyleSheet('background-color : black')  # Fond noir pour le widget
        # self.head_widget.hide()  # Masquage initial du widget
        # self.extras_layout.addWidget(self.head_widget, 35)

        # # # Ajout du layout des extras à la grille principale
        # self.layout.addLayout(self.extras_layout, 1, 1, 1, 2)

    def addDevice(self, name : str, dev_type : str):
        """
        Parameters
        ----------
        name : str
            name of the specific device (ex: FAROS-299055).
        dev_type : str
            model of the device, is either 'faros' or 'pupil'.
        """

        self.control_panel.device_list.addDevice(name, dev_type)
        self.control_panel.device
        print(f"adding device {name} of type {dev_type}")
        if dev_type == "faros":
            self.faros_worker = FarosWorker(name, self)
            self.faros_thread = threading.Thread(target = self.faros_worker.receiveFaros)
            self.faros_thread.start()
            print("faros thread started")
            
        if dev_type == "pupil":
            self.control_panel.start_button.setDisabled(False)
            threading.Thread(target= self.update_PI_state).start()

# Code d'exécution principal
if __name__ == "__main__":
    
    freeze_support() #necessary on windows to not spawn a second app when a subprocess is launched
    sig = Signal()
    app = QApplication(sys.argv)  # Création de l'application Qt
    window = MainWindow()  # Instanciation de la fenêtre principale
    #window.move(0, 0)
    #window.move(1920, 0)
    #window.showMaximized()
    window.show()  # Affichage de la fenêtre
    sys.exit(app.exec_())  # Boucle d'événements de l'application
