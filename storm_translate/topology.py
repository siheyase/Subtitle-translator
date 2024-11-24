from pystorm.topology import Topology
from video_spout import VideoSpout
from preprocess_bolt import PreprocessBolt
from ocr_bolt import OCRBolt
from translate_bolt import TranslateBolt
from render_bolt import RenderBolt

class VideoTranslationTopology(Topology):
    spout = VideoSpout.spec(name="video-spout")
    preprocess = PreprocessBolt.spec(inputs=[spout], name="preprocess-bolt")
    ocr = OCRBolt.spec(inputs=[preprocess], name="ocr-bolt")
    translate = TranslateBolt.spec(inputs=[ocr], name="translate-bolt")
    render = RenderBolt.spec(inputs=[translate], name="render-bolt")
