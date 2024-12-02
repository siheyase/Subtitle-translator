import cv2
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def overlay_subtitles(frame_path, subtitle, output_path):
    # 打开帧图像
    frame = Image.open(frame_path)
    draw = ImageDraw.Draw(frame)

    # 加载字体并设置大小
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/SourceHanSerifSC-VF.ttf", 20)
    except IOError:
        print("字体加载失败，请检查字体路径")
        font = ImageFont.load_default()

    # 获取文本的尺寸
    text_bbox = draw.textbbox((0, 0), subtitle, font=font)  # 返回文本的边界框
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    # 计算文本的起始位置，使其居中
    width, height = frame.size
    x = (width - text_width) // 2  # 水平居中
    y = 10  # 垂直位置（距离顶部20像素）

    # 在图像上绘制文本
    draw.text((x, y), subtitle, font=font, stroke_width=0.5)

    # 保存带字幕的帧
    frame.save(output_path)


# 合成视频帧与字幕的函数
def combine_frames_with_subtitles(frame_dir, subtitle_file, output_dir):
    # 读取字幕文件并处理异常行
    subtitles = {}
    for filename in os.listdir(subtitle_file):
        if filename.startswith('part-'):
            file_path = os.path.join(subtitle_file, filename)
            with open(file_path, "r") as f:
                for line in f:
                    if not line.strip():  # 跳过空行
                        continue
                    parts = line.split(",", 1)
                    if len(parts) < 2:  # 跳过格式错误的行
                        print(f"Skipping invalid line: {line.strip()}")
                        continue
                    frame_name = parts[0].replace("frames_preprocessed/", "").strip()
                    subtitle_text = parts[1].strip()
                    subtitles[frame_name] = subtitle_text
                    # subtitles[parts[0]] = parts[1].strip()

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 在帧上叠加字幕
    for frame in os.listdir(frame_dir):
        frame_path = os.path.join(frame_dir, frame)
        if frame not in subtitles:
            print(f"No subtitle for frame {frame}, skipping...")
            continue
        subtitle = subtitles[frame]

        img = cv2.imread(frame_path)
        if img is None:
            print(f"Failed to read {frame_path}, skipping...")
            continue

        # 调用 overlay_subtitles 函数叠加字幕
        output_path = os.path.join(output_dir, frame)
        overlay_subtitles(frame_path, subtitle, output_path)

if __name__ == "__main__":
    combine_frames_with_subtitles("frames_preprocessed", "translated_subtitles", "frames_with_subtitles")
