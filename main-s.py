import numpy as np
import cv2
import time

class Circle():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 0
        self.count = 0
        self.drop = False

    def update(self):
        self.count += 1
        self.r += 1
        if self.count > 50:
            self.drop = True

new_circle = Circle(50, 50)
circles = []
circles.append(new_circle)
for i in range(1000):
    img = np.full((100, 100, 3), 255, dtype=np.uint8)
    for j, circle in enumerate(circles):
        circle.update()
        if circle.drop:
            circles.pop(j)
            continue
        cv2.circle(img, (circle.x, circle.y), circle.r, (0, 0, 0), thickness=3, lineType=cv2.LINE_AA)
    cv2.imshow('img', img)
    cv2.waitKey(1000//60)
