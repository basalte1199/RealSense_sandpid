from re import A
import pyrealsense2 as rs
import numpy as np
import numpy
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

cnt = 0
depth = {}
while True:
        frames = pipe.wait_for_frames()

        # frameデータを取得
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        depth_colormap = np.zeros((1980, 1080, 3), np.uint8)
        
        # 画像データに変換
        #color_image = np.asanyarray(color_frame.get_data())
        # 距離情報をカラースケール画像に変換する
        #depth_color_frame = rs.colorizer().colorize(depth_frame)
        #depth_image = np.asanyarray(depth_color_frame.get_data())
        x_data = 0
        while True:
            a = depth_frame.get_distance(x_data,400)   #横一列のdepthデータ読み出し
            depth_data = math.floor(a * 10 ** 4) / (10 ** 4)
            if depth.get(x_data) != depth_data and int(depth_data) != 0 and int(depth_data) != 1:
                #print(abs(115 - (x_data // 11)) ** 2)
                #print((depth_data*100) ** 2)
                f = ((depth_data / 10) ** 2) - (57 - (x_data // 11) ** 2)   #単位cm
                if f >= 1:
                    h = 720 - (math.sqrt(f) - 60)  #y座標
                m = math.floor(h * 10 ** 2) / (10 ** 2)   #小数点2以下切り捨て
                wind_x =  m * 11
                wind_y = h
                print(wind_x,wind_y,x_data,m,f,a,depth_data)
                if wind_x >= 720 or wind_x <= 0 or wind_y >= 1280 or wind_y <= 0:
                    break
                else:
                    print("hi")
            
            depth.update({x_data:depth_data})
            x_data+=1

            if x_data == 1280:   #一列読み込んだらまた最初から読み込む
                break
            #print(x_data,depth_data)

        
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', depth_colormap)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
