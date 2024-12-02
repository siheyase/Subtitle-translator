# Spark 提交作业主程序
import os
from extract_frames import extract_frames
from preprocess_frames import preprocess_frame
from ocr_and_translate import ocr_and_translate
from combine_video import combine_frames_with_subtitles

if __name__ == "__main__":
    # 提取帧
    extract_frames("input_video/video.mp4", "frames")

    # 预处理帧
    preprocess_frame("frames", "frames_preprocessed")

    # OCR 和翻译（通过 Spark 提交）
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("Subtitle Translation").getOrCreate()
    sc = spark.sparkContext
    frame_paths = [f"frames_preprocessed/{frame}" for frame in os.listdir("frames_preprocessed")]
    # frame_paths = list(set([f"frames_preprocessed/{frame}" for frame in os.listdir("frames_preprocessed") if frame.endswith(".jpg")]))
    print(f"Unique frame paths: {len(frame_paths)}")
    num_partitions = min(len(frame_paths), 8)  # 根据帧数量动态设置分区
    rdd = sc.parallelize(frame_paths, numSlices=num_partitions)
    # rdd = sc.parallelize(frame_paths)

    # translated_rdd = rdd.map(lambda frame: ocr_and_translate(frame)).filter(lambda x: x is not None)
    translated_rdd = rdd.map(lambda frame: (frame, ocr_and_translate(frame)))
    # translated_rdd = rdd.map(lambda frame: (os.path.basename(frame), ocr_and_translate(frame)))
    # 确保保存格式为：帧文件名,字幕
    # translated_rdd = translated_rdd.map(lambda x: f"{x[0]},{x[1]}" if x[1] else None)
    translated_rdd = translated_rdd.map(lambda x: f"{x[0]},{x[1]}" if x[1] else None).filter(lambda x: x is not None)
    
    results = translated_rdd.collect()  # 强制执行任务
    print(f"Total translated frames: {len(results)}")
    for res in results:
        print(res)  # 打印每个翻译的结果，检查数据是否正确
    # translated_rdd = rdd.map(lambda frame: (frame, ocr_and_translate(frame)))
    # print(translated_rdd.collect())  # 输出翻译结果

    translated_rdd.saveAsTextFile("file:///home/xuqi/video_subtitle_translation/translated_subtitles")
    # translated_rdd.saveAsTextFile("translated_subtitles")

    # 合成字幕
    combine_frames_with_subtitles("frames_preprocessed", "translated_subtitles", "frames_with_subtitles")

    # 重新合成视频
    print("All tasks completed!")
