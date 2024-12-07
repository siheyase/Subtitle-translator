from paddleocr import PaddleOCR

# 初始化 OCR 模型
ocr = PaddleOCR(use_gpu=False)

def perform_ocr(frame_path):
    """
    对图像帧进行OCR识别
    """
    try:
        result = ocr.ocr(frame_path, cls=True)
        if not result[0]:
            print(f"No text detected in frame {frame_path}, skipping...")
            return ""
        detected_texts = [line[1][0] for line in result[0]]
        text = "\n".join(detected_texts)
        print(f"Recognized text: {text}")
        return text
    except Exception as e:
        print(f"Error during OCR for frame {frame_path}: {e}")
        return ""
