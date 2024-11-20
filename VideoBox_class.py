from lib import PWidget

class VideoBox(PWidget):
    """
    Display widget for the scene video of the pupil neon
    """
    frames = []
    last_timestamp = 0
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        self.screen = QLabel("screen")
        self.screen.setAlignment(Qt.AlignCenter)
        self.screen.setStyleSheet(f'background-color: black')
        self.layout.addWidget(self.screen)
        self.screen.setPixmap(QPixmap(self.size()))
        
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.draw_frame)
        self.frame_timer.start(1000//16)
        
    def on_new_frame(self, frame_, gaze):
        """
        accumulate the few last frames and draw the gaze circle on them. I tried this structure when i had lag 
        issues in the video stream but i'm not sure it changed anything. 
        Drawing the frames directly worked too and may be just as good.
        
        Parameters
        ----------
        frame_ : 
            pupil api video frame object.
        gaze : TYPE
            pupil api gaze object.

        """
        frame = frame_.bgr_pixels
        
        #workaround for a bug where the pupil neon api send frames with too high resolution
        if frame.shape[:2] != (1200,1600):
            frame = cv2.resize(frame, (1600,1200))
        radius = win.control_panel.circle_size_slider.value()
        cv2.circle(frame, (int(gaze.x), int(gaze.y)),
                       radius=radius,
                       color=(0, 0, 255),
                       thickness=8)
        self.frames.append(frame)
        
        if len(self.frames) > 5:
            self.frames = self.frames[-5:]
        
    def draw_frame(self):
        """
        display the last frame received
        """
        start_time = time.time()
        if self.frames:
            frame = self.frames.pop(-1)
            h, w = frame.shape[:2]
            qimg = QImage(frame,w,h,QImage.Format_BGR888)
            self.screen.setPixmap(QPixmap.fromImage(qimg).scaled(self.screen.width(), self.screen.height(), transformMode=Qt.SmoothTransformation,
                                                       aspectRatioMode=Qt.KeepAspectRatio))
    
    
    def resizeEvent(self,e):
        self.screen.clear()
        print('resizing')
        super().resizeEvent(e)
