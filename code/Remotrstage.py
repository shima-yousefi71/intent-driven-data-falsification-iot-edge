import math
import time
from pathlib import Path
import base64
import os
import random
import traceback
list = [14]
#random.seed(42)
dedline_Info = {
    "yolov5x.pt": [14],
    "yolov5l.pt": [44],
    "yolov5m.pt": [40],
    "yolov5s.pt": [38]
}
app_info = {
    "yolov5x.pt": 0.1792 * (1) + 0.3923,
    "yolov5l.pt": 0.6390 * (1) + 1.274,
    "yolov5s.pt": 0.2354 * (1) + 0.3620,
    "yolov5m.pt": 0.1202 * (1) + 0.2280
}

server_app_info = {
    "yolov5m.pt": -0.07896+ 2.595,
    "yolov5l.pt": 0.06576*1 + 0.6831,
    "yolov5x.pt": 0.08880*1 + 0.1737,
    "yolov5s.pt": -0.1079*(1)+2.74

}

pow_info = {
    "yolov5x.pt": 179.3 * (1) + 5930,
    "yolov5l.pt": 362.8 * (1) + 9830,
    "yolov5s.pt": (402.8 * (1) + 5294),
    "yolov5m.pt": 169.1 * (1) + 4918
}


class First_stages:

    def __init__(self, model, device_ID):

        self.model = model
        self.device_ID = device_ID

        self.imgsz = 512
        # self.remote_r= None#save_data (msg["remote_r"])

        #self.deadline = list[random.randint(0,len(list)-1)]
        self.deadlinelist = dedline_Info[self.model]
        self.deadline = self.deadlinelist[random.randint(0,len(self.deadlinelist)-1)]
        #self.deadline=18
        # print("deadline=",self.deadline)
        print(f'stages_deadline={self.deadline}')

        self.total_fps = 30
        self.avg_pow = 0
        self.server = 0.5
        self.iteration = 0
        self.pre_u_segment = None

    def remote_stages(self):
        fps_max = round((self.deadline - self.total_fps * server_app_info[self.model]) / (
                app_info[self.model] - server_app_info[self.model]))
        self.fps = self.total_fps - fps_max
        print(f'Device maximum stages = {fps_max}')
        print(f'Server minimum stages = {self.fps} ')

        return (self.fps)


if __name__ == '__main__':
    r = First_stages()
    r.__init__()