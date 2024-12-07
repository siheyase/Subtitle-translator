import json
import os
import ollama

# 设置代理
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
os.environ["ALL_PROXY"] = "socks5://127.0.0.1:7891"

# 翻译逻辑
def translate_text(text):
    """
    使用翻译缓存和模型翻译文本
    """
    if not text.strip():
        print("Empty input text.")
        return ""

    print(f"Translating text: {text}")
    retry_times = 3
    for i in range(retry_times):
        response = ollama.generate(
            model='qwen2.5:1.5b-instruct-q8_0',
            prompt=f"""
                Translate the following English text into Chinese. Ensure the translation is accurate, contextually appropriate, and retains the original meaning and tone.
                Provide only the translation in simplified Chinese characters unless otherwise specified. Do not include any additional explanations, comments, text, or emojis in the output.  

                If the input text contains unusual special characters, inconsistent punctuation, emojis, or line breaks, follow these steps:  

                1. Remove or ignore any unusual special characters, emojis, redundant spaces, or other non-standard elements that disrupt the sentence flow.  
                2. Reconstruct and correct the text to form a coherent, grammatically correct, and contextually sensible sentence, using context to infer any unclear parts.  
                3. Translate the corrected text into Chinese, ensuring accuracy, tone, and consistency with the original intent.  

                Example for clarification:
                - Input text: "Th3 qu1ck bro@wn fo#x ju-mps ov3r thE la!zy d*g.-::---"  
                - Corrected text: "The quick brown fox jumps over the lazy dog."  
                - Translation result: "敏捷的棕色狐狸跳过了懒狗。"

                The text to translate is: {text}  
                Your translation result should be:
                """
        )
        translated_text = response.get('response', '').strip()
        if translated_text:
            return translated_text  
    return ""  