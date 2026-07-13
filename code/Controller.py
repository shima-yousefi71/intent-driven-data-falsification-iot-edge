"""
Controller.py

Controller logic for allocating edge-server capacity among collaborative
IoT-edge devices based on reported power and battery information.
"""
import traceback

Total_power_used=[]

BATT_INFO = {
    "yolov5x.pt": 40920,
    "yolov5l.pt": 21384,
    "yolov5s.pt": 15400,
    "yolov5m.pt": 30960
                    }
List = [15, 16, 17, 18]
APP_INFO = {
    "yolov5s.pt": 0.5,
    "yolov5x.pt": 0.55,
    "yolov5l.pt":0.6,
    "yolov5m.pt":0.7,
    "yolov5n.pt":0.75
}

SERVER_APP_INFO = {
    "yolov5s.pt": 0.065,
    "yolov5x.pt": 0.075,
    "yolov5l.pt":0.08,
    "yolov5m.pt":0.085,
    "yolov5n.pt":0.9
}


SERVER_APP_INFO = {
    "yolov5s.pt": 100,
    "yolov5x.pt": 150,
    "yolov5l.pt": 200,
    "yolov5m.pt": 240,
    "yolov5n.pt": 300
}

class Controller:

    def __init__(self,model,device_id,fps,alive):

                self.model = model
                self.device_id = device_id
                self.fps = fps
                self.imgsz= 512

                ## Total number of DNN partitions in the application.
                self.total_fps= 30

                # Total edge-server capacity available across all devices.
                self.edge_total_fps = 72

                self.avg_pow = 0
                self.server = 0.5
                self.iteration = 0
                self.pre_u_segment= None
                
                # Initial battery level for this device model.
                self.Battery_level = BATT_INFO[self.model]
                
                self.remain_edge_fps =None
                self.TX2_fps = fps
                self.alive = alive


    def urb_to_device(self,used_fps,live):

        self.remain_edge_fps=self.edge_total_fps - used_fps
        if self.remain_edge_fps <0:
            self.remain_edge_fps=0
        print(f'remained server capacity = {self.remain_edge_fps}')
        return(self.remain_edge_fps)

    def new_fps(self,iteration,Power_list,tatal_Pcunsumtion, power_consum,battery):


                print(f'tx2 1 = {self.TX2_fps}')

                print(f'power_consum = {power_consum}')
                print(f' tatal_Pcunsumtion = {tatal_Pcunsumtion}')
                if iteration>=0:
                        #self.Battery_level = self.Battery_level - (power_consum)#battery level is actual
                        self.Battery_level=battery
                        print("Remaining battery level =", self.Battery_level)
                        print(f'Power_list = {Power_list}')
                if self.Battery_level > 0 :
                            if ((power_consum)/(self.Battery_level)) < 1 or ((power_consum)/(self.Battery_level))>0:
                                if Power_list !=0:
                                    print(f'second remain capacity of server = {self.remain_edge_fps}')
                                    if self.remain_edge_fps==72:
                                        print(f'alive = {self.alive}')
                                        self.fps= int(self.remain_edge_fps/self.alive)
                                        self.TX2_fps=0
                                        print('self , TX2 = ', self.fps,self.TX2_fps)
                                    else:
                                           self.fps=int((((Power_list/tatal_Pcunsumtion)* self.remain_edge_fps)))
                                           print(f'new server-capacity dedicated to device = {self.fps}')
                                    if (self.fps + self.TX2_fps) > 30:
                                        print("self fps after = ", self.fps)
                                        print("tx2 = ",self.TX2_fps)
                                        self.fps= self.total_fps - (self.TX2_fps)

                                        print(f'TX2-fps3 = {self.TX2_fps}')
                                        print("wwww ", self.fps)
                                    if self.fps>30:
                                        self.fps=30
                                        print(f'server caopacity after 30= {self.fps}')
                                else:
                                    pass
                            print(traceback.format_exc())
                            return(self.fps)







if __name__ == '__main__':
    r = controller()
    r.__init__()
#((Power_list*100)/(self.Battery_level))>0 and