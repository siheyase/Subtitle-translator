import cv2
import os
from PIL import Image, ImageDraw, ImageFont

def overlay_subtitles(frame_path, subtitle, output_path, font_path="/home/cqw/sparkproject/fonts/SourceHanSerifSC-VF.ttf", font_size=20):
    frame = Image.open(frame_path)
    draw = ImageDraw.Draw(frame)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font loading failed. Using default font.")
        font = ImageFont.load_default()

    # 获取文本的尺寸
    text_bbox = draw.textbbox((0, 0), subtitle, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    # x = (frame.width - text_width) // 2
    # y = frame.height - text_height - 20

    # draw.text((x, y), subtitle, font=font, fill="white")
    # 计算文本的起始位置，使其居中
    width, height = frame.size
    x = (width - text_width) // 2  # 水平居中
    y = 10  # 垂直位置（距离顶部20像素）

    # 在图像上绘制文本
    # draw.text((x, y), subtitle, font=font, stroke_width=0.5)
    draw.text((x, y), subtitle, font=font, fill="white", stroke_width=3, stroke_fill="black")
    

    # 保存带字幕的帧
    frame.save(output_path)




def combine_frames_with_subtitles(frame_dir, output_dir, grouped_sentences, font_path="/home/cqw/sparkproject/fonts/SourceHanSerifSC-VF.ttf"):
    """
    将字幕合并到帧图像上。
    :param frame_dir: 原始帧图像目录
    :param output_dir: 输出帧图像目录
    :param grouped_sentences: 分组后的句子字典
    :param font_path: 字体文件路径
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 加载字幕
    print("Loading subtitles...")
    frame_to_subtitle = {}

    for sentence, data in grouped_sentences.items():
        frames_id = data.get("frames_id", [])
        translate = data.get("translate", "")
        for frame_id in frames_id:
            frame_to_subtitle[frame_id] = translate

    print(f"Loaded {len(frame_to_subtitle)} subtitles for frames.")

    # 遍历帧图像，添加字幕
    for frame_file in os.listdir(frame_dir):
        if not frame_file.endswith((".jpg", ".png")):
            continue

        # 提取帧编号
        frame_id = int(frame_file.split("_")[1].split(".")[0])
        subtitle = frame_to_subtitle.get(frame_id, "")

        # 跳过无字幕的帧
        if not subtitle:
            continue

        # 路径定义
        frame_path = os.path.join(frame_dir, frame_file)
        output_frame_path = os.path.join(output_dir, frame_file)

        # 使用 overlay_subtitles 添加字幕
        try:
            overlay_subtitles(frame_path, subtitle, output_frame_path, font_path=font_path, font_size=20)
        except Exception as e:
            print(f"Error overlaying subtitles for frame {frame_path}: {e}")

    print(f"Frames with subtitles saved to {output_dir}.")

# def combine_frames_with_subtitles(frame_dir, subtitle_file, output_dir):
#     subtitles = {}# 存储 frame_name 和 subtitle
#     for filename in os.listdir(subtitle_file):
#         if filename.startswith('part-'):
#             with open(os.path.join(subtitle_file, filename), "r") as f:
#                 lines = [line.strip() for line in f if line.strip()]  # 去除空行并读取所有行
#                 current_frame_name = None  # 当前的 frame_name
#                 current_subtitle = []  # 当前 subtitle 列表，用于拼接多行

#                 for line in lines:
#                     # 检查是否是 frame_name 行
#                     if line.startswith("frame name:") and line.lower().endswith((".jpg", ".png")):
#                         # 如果已经有一个 frame_name，保存之前的 subtitle
#                         if current_frame_name:
#                             subtitles[current_frame_name] = "\n".join(current_subtitle)  # 提取 subtitle
                        
#                         # 更新新的 frame_name 和清空 subtitle
#                         current_frame_name = line[len("frame name:"):].strip()  # 提取 frame_name
#                         current_subtitle = []  # 清空 subtitle 列表
#                     else:
#                         # 如果不是 frame_name 行，将其作为 subtitle 内容
#                         current_subtitle.append(line[len("subtitle:"):].strip())

#                 # 保存最后一个 frame_name 和 subtitle
#                 if current_frame_name:
#                     subtitles[current_frame_name] = "\n".join(current_subtitle)
#                 # all_lines = "".join([line.strip() + "\n" for line in f if line.strip()])  # 拼接所有行
#                 # first_comma_index = all_lines.find(",")  # 找到第一个逗号的位置

#                 # if first_comma_index == -1:
#                     # 如果没有逗号，直接抛出异常终止程序
#                     # raise ValueError("The file does not contain a comma. Program terminated.")
                
#                 # 提取逗号之前的内容作为 frame_name
#                 # frame_name = all_lines[:first_comma_index].strip()
#                 # 提取逗号之后的内容作为 subtitle
#                 # subtitle = all_lines[first_comma_index + 1:].strip()
#                 # subtitles[frame_name] = subtitle
#                 # for line in f:
#                 #     if not line.strip():
#                 #         continue
#                 #     parts = line.split(",", 1)
#                 #     if len(parts) < 2:
#                 #         continue
#                 #     frame_name, subtitle = parts[0].strip(), parts[1].strip()
#                 #     subtitles[frame_name] = subtitle

#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     for frame in os.listdir(frame_dir):
#         frame_path = os.path.join(frame_dir, frame)
#         if frame not in subtitles:
#             continue
#         overlay_subtitles(frame_path, subtitles[frame], os.path.join(output_dir, frame))





# import cv2
# import os
# from PIL import Image, ImageDraw, ImageFont
# import numpy as np


# def overlay_subtitles(frame_path, subtitle, output_path):
#     # 打开帧图像
#     frame = Image.open(frame_path)
#     draw = ImageDraw.Draw(frame)

#     # 加载字体并设置大小
#     try:
#         font = ImageFont.truetype("/home/cqw/sparkproject/fonts/SourceHanSerifSC-VF.ttf", 20)
#     except IOError:
#         print("字体加载失败，请检查字体路径")
#         font = ImageFont.load_default()

#     # 获取文本的尺寸
#     text_bbox = draw.textbbox((0, 0), subtitle, font=font)  # 返回文本的边界框
#     text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

#     # 计算文本的起始位置，使其居中
#     width, height = frame.size
#     x = (width - text_width) // 2  # 水平居中
#     y = 10  # 垂直位置（距离顶部20像素）

#     # 在图像上绘制文本
#     draw.text((x, y), subtitle, font=font, stroke_width=0.5)

#     # 保存带字幕的帧
#     frame.save(output_path)


# # 合成视频帧与字幕的函数
# def combine_frames_with_subtitles(frame_dir, subtitle_file, output_dir):
#     # 读取字幕文件并处理异常行
#     subtitles = {}
#     for filename in os.listdir(subtitle_file):
#         if filename.startswith('part-'):
#             file_path = os.path.join(subtitle_file, filename)
#             with open(file_path, "r") as f:
#                 for line in f:
#                     if not line.strip():  # 跳过空行
#                         continue
#                     parts = line.split(",", 1)
#                     if len(parts) < 2:  # 跳过格式错误的行
#                         print(f"Skipping invalid line: {line.strip()}")
#                         continue
#                     frame_name = parts[0].replace("frames_preprocessed/", "").strip()
#                     subtitle_text = parts[1].strip()
#                     subtitles[frame_name] = subtitle_text
#                     # subtitles[parts[0]] = parts[1].strip()

#     # 创建输出目录
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # 在帧上叠加字幕
#     for frame in os.listdir(frame_dir):
#         frame_path = os.path.join(frame_dir, frame)
#         if frame not in subtitles:
#             print(f"No subtitle for frame {frame}, skipping...")
#             continue
#         subtitle = subtitles[frame]

#         img = cv2.imread(frame_path)
#         if img is None:
#             print(f"Failed to read {frame_path}, skipping...")
#             continue

#         # 调用 overlay_subtitles 函数叠加字幕
#         output_path = os.path.join(output_dir, frame)
#         overlay_subtitles(frame_path, subtitle, output_path)

# if __name__ == "__main__":
#     combine_frames_with_subtitles("frames_preprocessed", "translated_subtitles", "frames_with_subtitles")
