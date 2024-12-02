# 帧预处理脚本
import cv2
import os

def preprocess_frame(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for frame_file in os.listdir(input_dir):
        frame_path = os.path.join(input_dir, frame_file)
        frame = cv2.imread(frame_path)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized_frame = cv2.resize(gray_frame, (640, 360))
        cv2.imwrite(os.path.join(output_dir, frame_file), resized_frame)

if __name__ == "__main__":
    preprocess_frame("frames", "frames_preprocessed")
