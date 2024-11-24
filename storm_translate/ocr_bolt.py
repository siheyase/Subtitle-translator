from pystorm.bolt import Bolt
import easyocr

class OCRBolt(Bolt):
    def initialize(self, stormconf, context):
        self.reader = easyocr.Reader(['en'])

    def process(self, tup):
        frame = tup.values[0]
        if frame == "STOP":
            self.emit([frame, None])
        else:
            # OCR 识别
            results = self.reader.readtext(frame, detail=0)
            text = " ".join(results) if results else ""
            self.emit([frame, text])
