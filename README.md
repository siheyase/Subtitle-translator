#### 项目结构

```
.
├── frames/                           # 提取出来的视频帧
├── frames_preprocessed/              # 预处理结束的视频帧
├── translated_subtitles/             # 字幕翻译任务分区输出结果
├── frames_with_subtitles/            # 翻译后的字幕合并视频帧
├── input_video # 要处理的视频放在这里
│   ├── video-all.mp4
│   └── video.mp4 # 命名为video.mp4 是待处理的视频
├── combine_video.py # 合并翻译后的字幕和视频帧
├── extract_frames.py # 帧提取
├── ocr_and_translate.py # # 字幕识别和翻译
├── preprocess_frames.py # 帧预处理
└── spark_job.py # Spark 提交作业主程序
```

#### 项目构建
**1. Apache Spark**  

**2. python依赖**  
requirement.txt # 待构建
```
easyocr
opencv
pillow
transformers
```

**2. 中文字体**
可以替换为系统中已有的中文字体，我没有所以自己另外下了一个。
https://github.com/adobe-fonts/source-han-serif/raw/release/Variable/TTF/SourceHanSerifSC-VF.ttf
在`combine_video.py`文件line 14行处进行替换
```
font = ImageFont.truetype("/usr/share/fonts/truetype/SourceHanSerifSC-VF.ttf", 20)
```

#### 运行命令
1. 启动Spark
```
start-master.sh
start-worker.sh spark://<master-ip>:7077 # master-ip我这里单机部署就是localhost
```
2. 一些路径修改
`spark_job.py` line 40 这里翻译后的结果要存储在本地，因为我没用hadoop，改成项目绝对路径不容易报错
```
translated_rdd.saveAsTextFile("file:///home/xuqi/video_subtitle_translation/translated_subtitles")
```
3. 提交作业到Spark
**每次运行前，项目路径下 translated_subtitles 这个目录若是有输出文件必须删除干净，直接删掉 translated_subtitles 整个目录就行**  
运行后各个子目录都会自动生成
```
spark-submit --master local[4] spark_job.py
```


