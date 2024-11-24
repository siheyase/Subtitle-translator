from pystorm.bolt import Bolt
import cv2

class PreprocessBolt(Bolt):
    def process(self, tup):
        frame = tup.values[0]
        if frame == "STOP":
            self.emit([frame])
        else:
            # 转灰度并缩放
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized_frame = cv2.resize(gray_frame, (640, 360))
            self.emit([resized_frame])
