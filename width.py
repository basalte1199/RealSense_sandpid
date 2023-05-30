import pyrealsense2 as rs
import numpy as np
import cv2

# D435 Settings
RS_WIDTH = 848
RS_HEIGHT = 480
TARGET_DISTANCE = 30
align = rs.align(rs.stream.color)
pipe = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.depth, RS_WIDTH, RS_HEIGHT,  rs.format.z16, 90)
cfg.enable_stream(rs.stream.color, RS_WIDTH, RS_HEIGHT, rs.format.bgr8, 60)
profile = pipe.start(cfg)
intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
distance_max = TARGET_DISTANCE/depth_scale

# Screen Settings
cv2.namedWindow("screen", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("screen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
screen = cv2.imread("image.jpg", -1)
height, width, channels = screen.shape[:3]
SC_WIDTH = 1530 # mm
SC_HEIGHT = 870 # mm
SC_CENTER_X = int(SC_WIDTH/2)
SC_CENTER_Y = int(SC_HEIGHT/2)

SC_IMAGE_WIDTH = 854 # pix
SC_IMAGE_HEIGHT = 480 # pix
SC_IMAGE_CENTER_X = int(SC_IMAGE_WIDTH/2)
SC_IMAGE_CENTER_Y = int(SC_IMAGE_HEIGHT/2)

X_MIN = int(-SC_WIDTH/2)
X_MAX = int(SC_WIDTH/2)
Z_MIN = 1280
Z_MAX = Z_MIN + SC_HEIGHT
OFFSET_X = 20
OFFSET_Z = 110

while True:
    frames = pipe.wait_for_frames()
    aligned_frames = align.process(frames)
    color_frame = aligned_frames.get_color_frame()
    depth_frame = aligned_frames.get_depth_frame()
    if not depth_frame or not color_frame:
        continue

    color_image = np.asanyarray(color_frame.get_data())
    depth_image = np.asanyarray(depth_frame.get_data())

    scan_pts = []
    for uy in range(RS_HEIGHT):
        if uy == int(RS_HEIGHT/2) - 7:
            for ux in range(RS_WIDTH):
                z = depth_frame.get_distance(ux, uy)   #深度情報取得
                x = (float(ux) - intr.ppx) * z / intr.fx   #深度からタッチパネル上の座標を取得
                y = (float(uy) - intr.ppy) * z / intr.fy
                scan_pts.append([x, y, z])

    sc_image = np.zeros((SC_IMAGE_HEIGHT, SC_IMAGE_WIDTH, 3), np.uint8) #黒い画面を壁の大きさに合わせて生成
    for p in scan_pts:
        y = p[1]*1000
        if abs(y) < 1:
            x = -p[0]*1000 + OFFSET_X
            z =  p[2]*1000 + OFFSET_Z
            if abs(x) < X_MAX:
                if z > Z_MIN and z < Z_MAX:
                    ux = int((x + X_MAX) / SC_WIDTH * SC_IMAGE_WIDTH)
                    uy = SC_IMAGE_HEIGHT - int((z - Z_MIN) / SC_HEIGHT * SC_IMAGE_HEIGHT)   #計算
                    if ux >= 0 and ux <= SC_IMAGE_WIDTH and uy >= 0 and uy < SC_IMAGE_HEIGHT:
                        sc_image[uy, ux, 0] = 255 # B
                        sc_image[uy, ux, 1] = 255 # G
                        sc_image[uy, ux, 2] = 255 # R

    cv2.imshow("screen", sc_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break