import os
# import pytesseract
from paddleocr import PaddleOCR, draw_ocr
import hashlib
import ollama
from PIL import Image

# 设置代理
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
os.environ["ALL_PROXY"] = "socks5://127.0.0.1:7891"

# 已处理帧的缓存
processed_frames = set()
# 初始化 OCR 模型
ocr = PaddleOCR(use_gpu=False)  # 如果有 GPU，设置 use_gpu=True
# 配置 pytesseract（如果需要指定 tesseract 路径）
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"  # 根据系统路径修改

def translate_text(text):
    """
    使用 Ollama API 翻译文本
    """
    if not text.strip():
        print(f"input text is null:{text}")
        return ""
    
    retry_times = 3
    for i in range(retry_times):
        response = ollama.generate(
            # model='llama3:8b',
            model='qwen2.5:1.5b-instruct-q8_0',
            prompt=f"""
                Translate the following English text into Chinese. Ensure the translation is accurate, contextually appropriate, and retains the original meaning and tone.
                Provide only the translation in simplified Chinese characters unless otherwise specified. Do not include any additional explanations, comments, text, or emojis in the output.  

                If the input text contains unusual special characters, inconsistent punctuation, emojis, or line breaks, follow these steps:  
                1. Remove or ignore any unusual special characters, emojis, redundant spaces, or other non-standard elements that disrupt the sentence flow.  
                2. Reconstruct and correct the text to form a coherent, grammatically correct, and contextually sensible sentence, using context to infer any unclear parts.  
                3. Translate the corrected text into Chinese, ensuring accuracy, tone, and consistency with the original intent.  

                Example for clarification:
                - Input text: `"Th3 qu1ck bro@wn fo#x ju-mps ov3r thE la!zy d*g.-::---"`  
                - Corrected text: `"The quick brown fox jumps over the lazy dog."`  
                - Translation result: `"敏捷的棕色狐狸跳过了懒狗。"`

                The text to translate is: `{text}`  
                Your translation result should be:
                """

        )
        translated_text = response.get('response', '').strip()
        if translated_text:
            return translated_text
    return ""

def ocr_and_translate(frame_path):
    """
    对帧进行 OCR 和翻译
    """
    frame_hash = hashlib.md5(frame_path.encode()).hexdigest()
    if frame_hash in processed_frames:
        print(f"Skipping already processed frame: {frame_path}")
        return None

    print(f"Processing frame: {frame_path}")

    # 使用 pytesseract 读取图像中的文字
    try:
        # image = Image.open(frame_path)
        # text = pytesseract.image_to_string(image)
        result = ocr.ocr(frame_path, cls=True)
        if not result[0]:
            print(f"No text detected in frame {frame_path}, skipping...")
            return ""
        else:
            # 提取所有识别到的字符串
            detected_texts = [line[1][0] for line in result[0]]  # 获取识别到的文字
            # 按换行符拼接成一个完整的字符串
            text = "\n".join(detected_texts)
            print(f"Recognized text:{text}")
    except Exception as e:
        print(f"Error processing frame {frame_path}: {e}")
        return None

    # if not text.strip():
        # print(f"No text detected in frame {frame_path}, skipping...")
        # return None

    # 翻译文字
    translated_text = translate_text(text)
    print(f"{frame_path} Translated text: {translated_text}")
    # 缓存已处理帧
    processed_frames.add(frame_hash)
    return translated_text

if __name__ == "__main__":
    print("Testing OCR and translation pipeline...")
    # 测试 OCR 和翻译
    test_frame_path = "frames_preprocessed/frame_0000.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")
    test_frame_path = "frames_preprocessed/frame_0001.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")
    test_frame_path = "frames_preprocessed/frame_0002.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")
    test_frame_path = "frames_preprocessed/frame_0003.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")
    test_frame_path = "frames_preprocessed/frame_0004.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")
    test_frame_path = "frames_preprocessed/frame_0005.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")
    test_frame_path = "frames_preprocessed/frame_0006.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")
    test_frame_path = "frames_preprocessed/frame_0007.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")
    test_frame_path = "frames_preprocessed/frame_0008.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")
    test_frame_path = "frames_preprocessed/frame_0009.jpg"  # 替换为你的测试图片路径
    result = ocr_and_translate(test_frame_path)
    print(f"{test_frame_path} Translated text: {result}")

# import os
# import easyocr
# import hashlib
# import ollama
# import hashlib
# # 设置代理
# os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
# os.environ["ALL_PROXY"] = "socks5://127.0.0.1:7891"

# # 已处理帧的缓存
# processed_frames = set()
# reader = easyocr.Reader(['en'])  # 初始化 OCR 引擎

# def translate_text(text):
#     """
#     使用 Ollama API 翻译文本
#     """
#     if not text.strip():
#         return ""
    
#     retry_times = 3
#     for i in range(retry_times):
#         response = ollama.generate(
#             model='llama3:8b',
#             prompt=f"""
#             Translate the following English text into Chinese. Ensure the translation is accurate, 
#             contextually appropriate, and retains the original meaning and tone.
#             The text to translate is: {text}.
#             Your translation result should be:
#             """
#         )
#         translated_text = response.get('response', '').strip()
#         if translated_text:
#             return translated_text
#     return ""

# def ocr_and_translate(frame_path):
#     """
#     对帧进行 OCR 和翻译
#     """
#     frame_hash = hashlib.md5(frame_path.encode()).hexdigest()
#     if frame_hash in processed_frames:
#         print(f"Skipping already processed frame: {frame_path}")
#         return None

#     print(f"Processing frame: {frame_path}")
#     results = reader.readtext(frame_path, detail=0)
#     text = " ".join(results)
#     translated_text = translate_text(text)

#     if not text.strip():
#         print(f"No text detected in frame {frame_path}, skipping...")
#         return None

#     processed_frames.add(frame_hash)
#     return translated_text

# if __name__ == "__main__":
#     print("Testing OCR and translation pipeline...")
#     test_text = "The quick brown fox jumps over the lazy dog."
#     print(f"Translated text: {translate_text(test_text)}")


# # 字幕识别和翻译脚本
# import os
# import easyocr
# # from transformers import MarianMTModel, MarianTokenizer
# import hashlib
# import ollama

# os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
# os.environ["ALL_PROXY"] = "socks5://127.0.0.1:7891"

# # 缓存处理过的帧
# processed_frames = set()
# # 初始化
# reader = easyocr.Reader(['en'])
# # model_name = "Helsinki-NLP/opus-mt-en-zh"
# # tokenizer = MarianTokenizer.from_pretrained(model_name)
# # model = MarianMTModel.from_pretrained(model_name)

# def translate_text(text):
#     retry_times = 3
#     print(f"input text:{text}")
#     if not text.strip():
#         return ""
#     for i in range(retry_times):
#         response = ollama.generate(
#                     model='llama3:8b',
#                     prompt=(
#                     f"""
#                     Translate the following English text into Chinese. Ensure the translation is accurate, 
#                     contextually appropriate, and retains the original meaning and tone. Provide only the 
#                     translation in simplified Chinese characters unless otherwise specified. Do not include 
#                     any additional explanations, comments, or text beyond the translation result. 

#                     For example:
#                     If the text to translate is: "The quick brown fox jumps over the lazy dog."
#                     Your translation result should be: "敏捷的棕色狐狸跳过了懒狗。"

#                     The text to translate is: {text}.
#                     Your translation result should be:
#                     """
#                     )
#                 )
#         translated_text = response['response'].strip()
#         if translated_text:
#             print(f"translated_text:{translated_text}")
#             return translated_text
#         print(f"translated_text is:{translated_text},retry times{i+1}...")
#     return "translated_text is null"

# #def translate_text(text):
# #    if not text:
# #        return ""
# #    inputs = tokenizer(text, return_tensors="pt", padding=True)
# #    translated = model.generate(**inputs)
# #    return tokenizer.decode(translated[0], skip_special_tokens=True)

# # def ocr_and_translate(frame_path):
# #     results = reader.readtext(frame_path, detail=0)
# #     text = " ".join(results)
# #     translated_text = translate_text(text)
# #     return translated_text

# # def ocr_and_translate(frame_path):
# #     print(f"Processing frame: {frame_path}")
# #     results = reader.readtext(frame_path, detail=0)
# #     print(f"OCR results: {results}")
# #     text = " ".join(results)
# #     translated_text = translate_text(text)
# #     print(f"Translated text: {translated_text}")
# #     return translated_text

# def ocr_and_translate(frame_path):
#     # 计算帧的唯一哈希值
#     frame_hash = hashlib.md5(frame_path.encode()).hexdigest()
#     if frame_hash in processed_frames:
#         print(f"Skipping already processed frame: {frame_path}")
#         return None

#     print(f"Processing frame: {frame_path}")
#     results = reader.readtext(frame_path, detail=0)
#     print(f"OCR results: {results}")
#     text = " ".join(results)
#     translated_text = translate_text(text)
#     print(f"Translated text: {translated_text}")

#     if not results:
#         print(f"Skipping empty frame: {frame_path}")
#         return None
#     else:
#     # 记录处理过的帧
#         processed_frames.add(frame_hash)
#         return translated_text


# if __name__ == "__main__":
#     from pyspark.sql import SparkSession

#     spark = SparkSession.builder.appName("OCR and Translate").getOrCreate()
#     sc = spark.sparkContext

#     # 将帧路径并行化
#     frame_paths = [f"frames_preprocessed/{frame}" for frame in os.listdir("frames_preprocessed")]
#     rdd = sc.parallelize(frame_paths)

#     # 进行 OCR 和翻译
#     translated_rdd = rdd.map(lambda frame: (frame, ocr_and_translate(frame)))
#     translated_rdd.saveAsTextFile("translated_subtitles")

#     print("Testing tokenizer and model...")
#     test_text = "Hello, how are you?"
#     translated_text = translate_text(test_text)
#     print(f"Translated Text: {translated_text}")
