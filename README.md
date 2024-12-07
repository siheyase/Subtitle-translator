#### 项目结构

```
.
├── frames/                           # 提取出来的视频帧
├── frames_preprocessed/              # 预处理结束的视频帧
├── translated_subtitles/             # 字幕翻译任务分区输出结果
├── frames_with_subtitles/            # 翻译后的字幕合并视频帧
├── input_video # 要处理的视频放在这里
│   └── video-all.mp4 # 待处理的视频
├── combine_video.py # 合并翻译后的字幕和视频帧
├── extract_frames.py # 帧提取
├── ocr.py # 字幕识别
├── translate.py # 字幕翻译
├── preprocess_frames.py # 帧预处理
└── spark_job.py # Spark 提交作业主程序
```

#### 项目构建
虚拟机分配磁盘建议50G，内存目前我的设定是13.3G
**1. Apache Spark**  

**2. python依赖**  
python基于paddleocr要求限制版本为3.7-3.9
requirement.txt # 待构建
```
opencv-python
ollama
httpx[socks]
```

**2. 中文字体**
可以替换为系统中已有的中文字体，我没有所以自己另外下了一个。
https://github.com/adobe-fonts/source-han-serif/raw/release/Variable/TTF/SourceHanSerifSC-VF.ttf
在`combine_video.py`文件line 14行处进行替换
```
font = ImageFont.truetype("/usr/share/fonts/truetype/SourceHanSerifSC-VF.ttf", 20)
```

**3.PaddleOCR文本检测**
安装源选择清华，CPU版PaddlePaddle：
```
python -m pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**4.Ollama安装和模型下载**
在linux系统安装ollama
```
curl -fsSL https://ollama.com/install.sh | sh
```
ollama服务启动
```
ollama serve
```
选择qwen2.5:1.5b-instruct-q8_0模型作为翻译模型（约1.6G）
```
ollama run qwen2.5:1.5b-instruct-q8_0
```
第一次下载完成后会直接进入模型的命令行交互界面，可输入/bye退出
后续通过仍通过该命令启动模型
```
ollama run <model_name>
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
ps：cqw的输入命令是这个，可以尝试换不同的并行数和分区看看运行效率。（目前对于12秒的video-all.mp4，单机可以在3min内运行完）
```
spark-submit --master local[4] --conf spark.default.parallelism=8 --conf spark.sql.shuffle.partitions=8 spark_job.py
```


