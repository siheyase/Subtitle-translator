from pystorm.bolt import Bolt
import cv2

class RenderBolt(Bolt):
    def process(self, tup):
        frame, original_text, translated_text = tup.values
        if frame == "STOP":
            self.emit(["STOP"])
        else:
            if translated_text:
                # 在帧上叠加字幕
                cv2.putText(frame, translated_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            self.emit([frame])
