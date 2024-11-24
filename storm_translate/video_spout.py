from pystorm.spout import Spout
import cv2

class VideoSpout(Spout):
    def initialize(self, stormconf, context):
        self.video_path = stormconf.get("video_path", "video.mp4")
        self.capture = cv2.VideoCapture(self.video_path)
    
    def next_tuple(self):
        ret, frame = self.capture.read()
        if ret:
            self.emit([frame])
        else:
            self.capture.release()
            self.emit(["STOP"])
