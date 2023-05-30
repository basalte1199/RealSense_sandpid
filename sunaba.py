import pyrealsense2 as rs
import numpy as np
import cv2
import math

# カメラの設定
conf = rs.config()
# RGB
conf.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
# 距離
conf.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

# stream開始
pipe = rs.pipeline()
profile = pipe.start(conf)

while True:
    frames = pipe.wait_for_frames()

    # frameデータを取得
    color_frame = frames.get_color_frame()
    depth_frame = frames.get_depth_frame()

    # 画像データに変換
    color_image = np.asanyarray(color_frame.get_data())
    depth_image = np.asanyarray(depth_frame.get_data())

    # 50cmから1mの範囲でデプスマップの最大値・最小値を計算
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    depth_min = 500
    depth_max = 800
    depth_range = depth_max - depth_min

    # 距離情報をカラースケール画像に変換する
    for y in range(depth_colormap.shape[0]):
        for x in range(depth_colormap.shape[1]):
            depth = depth_image[y, x]
            if depth < depth_min or depth > depth_max:
                depth_colormap[y, x, :] = [0, 0, 0]
            else:
                depth_norm = (depth - depth_min) / depth_range
                r = np.clip(255 * (1 - depth_norm), 0, 255)
                b = np.clip(255 * depth_norm, 0, 255)
                g = 0
                depth_colormap[y, x, :] = [b, g, r]

    # ウィンドウに表示
    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', depth_colormap)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 終了処理
pipe.stop()
cv2.destroyAllWindows()