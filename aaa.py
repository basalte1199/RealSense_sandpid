import cv2
import numpy as np
import pyrealsense2 as rs

# RealSenseカメラの設定
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# 色分けの設定
colors = np.zeros((640, 480, 3), np.uint8)

# スキャンする範囲の設定
min_distance = 0.03  # 3cm
max_distance = 2.0  # 2m

try:
    while True:
        # フレームの取得
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        # 画像をNumpy配列に変換
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # 範囲外の距離に0を代入
        depth_image = np.where((depth_image > min_distance) & (depth_image < max_distance), depth_image, 0)

        # 3cmごとに色を分ける
        for i in range(0, 640, 3):
            for j in range(0, 480, 3):
                distance = depth_image[i, j]
                if distance == 0:
                    colors[i, j] = [0, 0, 0]
                else:
                    r = int((distance / max_distance) * 255)
                    g = int((distance / max_distance) * 255)
                    b = int((distance / max_distance) * 255)
                    colors[i, j] = [b, g, r]

        # 結果を表示
        cv2.imshow("Depth Image", depth_image)
        cv2.imshow("Color Image", color_image)
        cv2.imshow("Colored Depth Image", colors)
        key = cv2.waitKey(1)
        if key == ord("q"):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()