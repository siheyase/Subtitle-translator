import cv2
import os

def preprocess_frame(input_dir, output_dir, resize_dim):
    """
    预处理视频帧：调整大小并进行灰度处理
    Args:
        input_dir (str): 输入帧目录
        output_dir (str): 输出帧目录
        resize_dim (tuple): 调整的目标尺寸
    """
    os.makedirs(output_dir, exist_ok=True)

    for frame_file in os.listdir(input_dir):
        frame_path = os.path.join(input_dir, frame_file)
        frame = cv2.imread(frame_path)

        if frame is None:
            print(f"Warning: Failed to read frame {frame_path}, skipping...")
            continue

        # 转为灰度图像
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 调整大小
        resized_frame = cv2.resize(gray_frame, resize_dim)

        # 保存处理后的帧
        cv2.imwrite(os.path.join(output_dir, frame_file), resized_frame)

    print(f"Preprocessed frames saved to {output_dir}")

if __name__ == "__main__":
    preprocess_frame("frames", "frames_preprocessed", (1280, 720))




# # 帧预处理脚本
# import cv2
# import os

# def preprocess_frame(input_dir, output_dir):
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#     for frame_file in os.listdir(input_dir):
#         frame_path = os.path.join(input_dir, frame_file)
#         frame = cv2.imread(frame_path)
#         gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         resized_frame = cv2.resize(gray_frame, (640, 360))
#         cv2.imwrite(os.path.join(output_dir, frame_file), resized_frame)

# if __name__ == "__main__":
#     preprocess_frame("frames", "frames_preprocessed")
