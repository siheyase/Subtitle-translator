from pystorm.bolt import Bolt
from transformers import MarianMTModel, MarianTokenizer

class TranslateBolt(Bolt):
    def initialize(self, stormconf, context):
        model_name = "Helsinki-NLP/opus-mt-en-zh"
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)

    def process(self, tup):
        frame, text = tup.values
        if frame == "STOP":
            self.emit([frame, text, None])
        elif text:
            # 翻译文本
            inputs = self.tokenizer(text, return_tensors="pt", padding=True)
            translated = self.model.generate(**inputs)
            translated_text = self.tokenizer.decode(translated[0], skip_special_tokens=True)
            self.emit([frame, text, translated_text])
        else:
            self.emit([frame, text, ""])
