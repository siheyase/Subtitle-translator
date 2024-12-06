import os
import cv2
import sys
from pyspark.sql import SparkSession
from pathlib import Path

# 动态获取用户目录和项目根目录
USER_HOME = Path.home()
PROJECT_ROOT = USER_HOME / "sparkproject" / "video_subtitle_translation"

# 添加项目路径到系统路径
sys.path.append(str(PROJECT_ROOT))

from extract_frames import extract_frames
from preprocess_frames import preprocess_frame
from ocr_and_translate import ocr_and_translate
from combine_video import combine_frames_with_subtitles

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
    input_video_path = PROJECT_ROOT / "input_video" / "video.mp4"
    frames_output_dir = PROJECT_ROOT / "frames"
    frames_preprocessed_dir = PROJECT_ROOT / "frames_preprocessed"
    subtitles_output_dir = PROJECT_ROOT / "translated_subtitles"
    final_video_path = PROJECT_ROOT / "output_video" / "final_video.mp4"

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
    num_partitions = min(len(frame_paths), 4)
    print(f"Using {num_partitions} partitions for parallel processing.")
    rdd = sc.parallelize(frame_paths, numSlices=num_partitions)

    # OCR 和翻译
    print("Step 6: Performing OCR and translation...")
    translated_rdd = (
        rdd.map(lambda frame: (frame, ocr_and_translate(frame)))
        .filter(lambda x: x[1] is not None)
        .map(lambda x: f"frame name:{os.path.basename(x[0])}\nsubtitle:{x[1]}")
    )

    # 保存翻译结果
    print("Step 7: Saving translated subtitles...")
    translated_rdd.saveAsTextFile(f"file://{subtitles_output_dir}")

    # 合成字幕到帧
    print("Step 8: Combining subtitles with frames...")
    combine_frames_with_subtitles(str(frames_preprocessed_dir), str(subtitles_output_dir), str(frames_output_dir))

    # 合成视频
    print("Step 9: Combining frames into video...")
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
