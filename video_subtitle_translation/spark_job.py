import os
import cv2
import sys
from pyspark.sql import SparkSession
from pathlib import Path
from extract_frames import extract_frames
from preprocess_frames import preprocess_frame
from ocr import perform_ocr
from translate import translate_text
from combine_video import combine_frames_with_subtitles

from collections import Counter
import json

# 动态获取用户目录和项目根目录
USER_HOME = Path.home()
PROJECT_ROOT = USER_HOME / "sparkproject" / "video_subtitle_translation"


def calculate_f1_score(s1, s2):
    """
    改进的 F1 值计算：基于字符频率统计，考虑重复字符。
    """
    # 统计每个字符出现的频率
    s1_counts = Counter(s1)
    s2_counts = Counter(s2)

    # 计算交集中每个字符的最小频率之和
    common_chars = set(s1_counts.keys()) & set(s2_counts.keys())
    common_count = sum(min(s1_counts[char], s2_counts[char]) for char in common_chars)

    # 计算 Precision 和 Recall
    precision = common_count / sum(s2_counts.values())
    recall = common_count / sum(s1_counts.values())

    # 避免分母为 0
    if precision + recall == 0:
        return 0.0

    # 计算 F1 值
    f1_score = 2 * (precision * recall) / (precision + recall)
    return f1_score

# 定义 OCR 处理逻辑
def process_ocr(frame_paths):
    """
    对帧进行 OCR 识别，返回帧编号和识别文本的字典
    """
    frame_dict = {}
    for frame_path in frame_paths:
        frame_name = os.path.basename(frame_path)
        frame_id = int(frame_name.split("_")[1].split(".")[0])  # 提取帧编号
        ocr_result = perform_ocr(frame_path)
        if ocr_result:
            frame_dict[frame_id] = ocr_result
    return frame_dict

# 定义分组逻辑
def group_frames_by_similarity(frame_dict, similarity_threshold=0.95):
    """
    根据帧编号和句子相似性分组句子
    """
    sorted_items = sorted(frame_dict.items(), key=lambda x: x[0])
    grouped_sentences = {}
    visited_frames = set()

    for frame_id, sentence in sorted_items:
        if frame_id in visited_frames:
            continue
        similar_frames = [frame_id]
        for other_frame_id, other_sentence in sorted_items:
            if other_frame_id <= frame_id or other_frame_id in visited_frames:
                continue
            f1_score = calculate_f1_score(sentence, other_sentence)
            if f1_score >= similarity_threshold:
                similar_frames.append(other_frame_id)
                visited_frames.add(other_frame_id)
        grouped_sentences[sentence] = {"frames_id": similar_frames}
    return grouped_sentences
# import os
# import cv2
# import sys
# from pyspark.sql import SparkSession
# from pathlib import Path

# # 动态获取用户目录和项目根目录
# USER_HOME = Path.home()
# PROJECT_ROOT = USER_HOME / "sparkproject" / "video_subtitle_translation"

# # 添加项目路径到系统路径
# sys.path.append(str(PROJECT_ROOT))

# from extract_frames import extract_frames
# from preprocess_frames import preprocess_frame
# # from ocr_and_translate import ocr_and_translate
# from combine_video import combine_frames_with_subtitles
# from ocr import perform_ocr
# from translate import load_translation_cache, translate_text

# # 初始化翻译缓存
# translation_cache = load_translation_cache()

# def ocr_and_translate(frame_path):
#     """
#     对帧进行OCR和翻译
#     """
#     # OCR识别
#     recognized_text = perform_ocr(frame_path)
#     if not recognized_text:
#         return None

#     # 翻译
#     translated_text = translate_text(recognized_text, translation_cache)
#     return translated_text


def get_video_dimensions(video_path):
    """
    获取视频的宽度和高度
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height


def combine_frames_into_video(frame_dir, output_video_path, fps):
    frame_files = sorted([
        os.path.join(frame_dir, frame)
        for frame in os.listdir(frame_dir)
        if frame.endswith((".jpg", ".png"))
    ])
    first_frame = cv2.imread(frame_files[0])
    height, width, _ = first_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for frame_file in frame_files:
        frame = cv2.imread(frame_file)
        video_writer.write(frame)

    video_writer.release()
    print(f"Final video saved at {output_video_path}")

if __name__ == "__main__":
    # 定义路径
    input_video_path = PROJECT_ROOT / "input_video" / "video-all.mp4"
    frames_output_dir = PROJECT_ROOT / "frames"
    frames_preprocessed_dir = PROJECT_ROOT / "frames_preprocessed"
    subtitles_output_dir = PROJECT_ROOT / "translated_subtitles"
    final_video_path = PROJECT_ROOT / "output_video" / "final_video-all.mp4"
    grouped_sentences_file = PROJECT_ROOT / "grouped_sentences.json"
    translated_subtitles_dir = PROJECT_ROOT / "translated_subtitles"

    # 确保必要的目录存在
    os.makedirs(frames_output_dir, exist_ok=True)
    os.makedirs(frames_preprocessed_dir, exist_ok=True)
    os.makedirs(final_video_path.parent, exist_ok=True)


    # 检测视频尺寸
    print("Step 1: Detecting video dimensions...")
    video_width, video_height = get_video_dimensions(str(input_video_path))
    print(f"Detected video dimensions: {video_width}x{video_height}")

    # 提取帧
    print("Step 2: Extracting frames...")
    extract_frames(str(input_video_path), str(frames_output_dir))

    # 预处理帧
    print("Step 3: Preprocessing frames...")
    preprocess_frame(str(frames_output_dir), str(frames_preprocessed_dir), (video_width, video_height))

    # 初始化 Spark
    print("Step 4: Initializing Spark session...")
    spark = SparkSession.builder.appName("Subtitle Translation").getOrCreate()
    sc = spark.sparkContext

    # 收集帧路径
    print("Step 5: Collecting frame paths...")
    frame_paths = [
        str(frames_preprocessed_dir / frame)
        for frame in os.listdir(frames_preprocessed_dir)
        if frame.endswith((".jpg", ".png"))
    ]
    print(f"Total frame paths: {len(frame_paths)}")

    # 设置分区数
    num_partitions = min(len(frame_paths), 8)
    print(f"Using {num_partitions} partitions for parallel processing.")
    rdd = sc.parallelize(frame_paths, numSlices=num_partitions)

    # # OCR 和翻译
    # print("Step 6: Performing OCR and translation...")
    # translated_rdd = (
    #     rdd.map(lambda frame: (frame, ocr_and_translate(frame)))
    #     .filter(lambda x: x[1] is not None)
    #     .map(lambda x: f"frame name:{os.path.basename(x[0])}\nsubtitle:{x[1]}")
    # )

    # # 保存翻译结果
    # print("Step 7: Saving translated subtitles...")
    # translated_rdd.saveAsTextFile(f"file://{subtitles_output_dir}")

    # # 合成字幕到帧
    # print("Step 8: Combining subtitles with frames...")
    # combine_frames_with_subtitles(str(frames_output_dir), str(subtitles_output_dir), str(frames_output_dir))

    print("Step 6: Performing OCR...")
    frame_dict_rdd = rdd.map(lambda frame_path: (frame_path, perform_ocr(frame_path))) \
                        .filter(lambda x: x[1] != "") \
                        .map(lambda x: (int(os.path.basename(x[0]).split("_")[1].split(".")[0]), x[1]))
    frame_dict = dict(frame_dict_rdd.collect())
    print(f"OCR completed. Recognized {len(frame_dict)} frames.")

    # Step 2: Group frames by similarity
    print("Step 7: Grouping frames by similarity...")
    grouped_sentences = group_frames_by_similarity(frame_dict)
    # save_grouped_sentences(grouped_sentences, grouped_sentences_file)
    # 将分组后的句子字典写入文件
    print(f"Saving grouped sentences to {grouped_sentences_file}...")
    with open(grouped_sentences_file, "w", encoding="utf-8") as f:
        json.dump(grouped_sentences, f, ensure_ascii=False, indent=4)
    print(f"Grouped sentences saved to {grouped_sentences_file}")

    # Step 3: Translation
    print("Step 8: Translating grouped sentences...")
    for sentence, data in grouped_sentences.items():
        if "translate" not in data:
            translation = translate_text(sentence)
            data["translate"] = translation
    print(f"Saving translations to {grouped_sentences_file}...")
    with open(grouped_sentences_file, "w", encoding="utf-8") as f:
        json.dump(grouped_sentences, f, ensure_ascii=False, indent=4)
    print(f"Translations saved to {grouped_sentences_file}")

    # Step 4: Combine subtitles and frames
    print("Step 9: Combining subtitles with frames...")
    combine_frames_with_subtitles(
    str(frames_output_dir),  # 原始帧目录
    str(frames_output_dir),        # 带字幕帧目录
    grouped_sentences              # 分组字幕字典
    )

    # 合成视频
    print("Step 10: Combining frames into video...")
    combine_frames_into_video(str(frames_output_dir), str(final_video_path), fps=30)
    print(f"Final video saved at: {final_video_path}")

    print("All tasks completed!")




# # Spark 提交作业主程序
# import os
# import sys
# sys.path.append('/home/cqw/sparkproject/video_subtitle_translation')
# from extract_frames import extract_frames
# from preprocess_frames import preprocess_frame
# from ocr_and_translate import ocr_and_translate
# from combine_video import combine_frames_with_subtitles




# if __name__ == "__main__":
#     # 提取帧
#     extract_frames("/home/cqw/sparkproject/video_subtitle_translation/input_video/video.mp4", "frames")

#     # 预处理帧
#     preprocess_frame("frames", "frames_preprocessed")

#     # OCR 和翻译（通过 Spark 提交）
#     from pyspark.sql import SparkSession

#     spark = SparkSession.builder.appName("Subtitle Translation").getOrCreate()
#     sc = spark.sparkContext
#     frame_paths = [f"frames_preprocessed/{frame}" for frame in os.listdir("frames_preprocessed")]
#     # frame_paths = list(set([f"frames_preprocessed/{frame}" for frame in os.listdir("frames_preprocessed") if frame.endswith(".jpg")]))
#     print(f"Unique frame paths: {len(frame_paths)}")
#     num_partitions = min(len(frame_paths), 8)  # 根据帧数量动态设置分区
#     rdd = sc.parallelize(frame_paths, numSlices=num_partitions)
#     # rdd = sc.parallelize(frame_paths)

#     # translated_rdd = rdd.map(lambda frame: ocr_and_translate(frame)).filter(lambda x: x is not None)
#     translated_rdd = rdd.map(lambda frame: (frame, ocr_and_translate(frame)))
#     # translated_rdd = rdd.map(lambda frame: (os.path.basename(frame), ocr_and_translate(frame)))
#     # 确保保存格式为：帧文件名,字幕
#     # translated_rdd = translated_rdd.map(lambda x: f"{x[0]},{x[1]}" if x[1] else None)
#     translated_rdd = translated_rdd.map(lambda x: f"{x[0]},{x[1]}" if x[1] else None).filter(lambda x: x is not None)
    
#     results = translated_rdd.collect()  # 强制执行任务
#     print(f"Total translated frames: {len(results)}")
#     for res in results:
#         print(res)  # 打印每个翻译的结果，检查数据是否正确
#     # translated_rdd = rdd.map(lambda frame: (frame, ocr_and_translate(frame)))
#     # print(translated_rdd.collect())  # 输出翻译结果

#     translated_rdd.saveAsTextFile("file:///home/cqw/sparkproject/video_subtitle_translation/translated_subtitles")
#     # translated_rdd.saveAsTextFile("translated_subtitles")

#     # 合成字幕
#     combine_frames_with_subtitles("frames_preprocessed", "translated_subtitles", "frames_with_subtitles")

#     # 重新合成视频
#     print("All tasks completed!")
