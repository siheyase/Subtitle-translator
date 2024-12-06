import cv2
import os

def extract_frames(video_path, output_dir):
    """
    提取视频帧并保存为图像文件
    """
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_path = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_count += 1

    cap.release()
    print(f"Extracted {frame_count} frames to {output_dir}")




# import cv2
# import os

# # 视频帧提取脚本
# def extract_frames(video_path, output_dir):
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#     cap = cv2.VideoCapture(video_path)
#     frame_count = 0
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         cv2.imwrite(f"{output_dir}/frame_{frame_count:04d}.jpg", frame)
#         frame_count += 1
#     cap.release()
#     print(f"Extracted {frame_count} frames to {output_dir}")

# if __name__ == "__main__":
#     extract_frames("input_video/video.mp4", "frames")
