# 字幕识别和翻译脚本
import os
import easyocr
from transformers import MarianMTModel, MarianTokenizer
import hashlib

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
os.environ["ALL_PROXY"] = "socks5://127.0.0.1:7890"

# 缓存处理过的帧
processed_frames = set()
# 初始化
reader = easyocr.Reader(['en'])
model_name = "Helsinki-NLP/opus-mt-en-zh"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate_text(text):
    if not text:
        return ""
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

# def ocr_and_translate(frame_path):
#     results = reader.readtext(frame_path, detail=0)
#     text = " ".join(results)
#     translated_text = translate_text(text)
#     return translated_text

# def ocr_and_translate(frame_path):
#     print(f"Processing frame: {frame_path}")
#     results = reader.readtext(frame_path, detail=0)
#     print(f"OCR results: {results}")
#     text = " ".join(results)
#     translated_text = translate_text(text)
#     print(f"Translated text: {translated_text}")
#     return translated_text

def ocr_and_translate(frame_path):
    # 计算帧的唯一哈希值
    frame_hash = hashlib.md5(frame_path.encode()).hexdigest()
    if frame_hash in processed_frames:
        print(f"Skipping already processed frame: {frame_path}")
        return None

    print(f"Processing frame: {frame_path}")
    results = reader.readtext(frame_path, detail=0)
    print(f"OCR results: {results}")
    text = " ".join(results)
    translated_text = translate_text(text)
    print(f"Translated text: {translated_text}")

    if not results:
        print(f"Skipping empty frame: {frame_path}")
        return None
    else:
    # 记录处理过的帧
        processed_frames.add(frame_hash)
        return translated_text


if __name__ == "__main__":
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("OCR and Translate").getOrCreate()
    sc = spark.sparkContext

    # 将帧路径并行化
    frame_paths = [f"frames_preprocessed/{frame}" for frame in os.listdir("frames_preprocessed")]
    rdd = sc.parallelize(frame_paths)

    # 进行 OCR 和翻译
    translated_rdd = rdd.map(lambda frame: (frame, ocr_and_translate(frame)))
    translated_rdd.saveAsTextFile("translated_subtitles")

    print("Testing tokenizer and model...")
    test_text = "Hello, how are you?"
    translated_text = translate_text(test_text)
    print(f"Translated Text: {translated_text}")
