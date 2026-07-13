"""
RootWidget.py

Device-side simulation model for the collaborative IoT-edge experiment.

This file models device energy consumption, local/edge partition execution,
battery updates, and the data falsification behavior used in the experiment.
"""
import random
import time
from concurrent.futures.thread import ThreadPoolExecutor
import numpy as np
from threading import Lock

m = Lock()

class RootWidget():
    
    def __init__(self, model, user, edge_fps, iteration):
                    # Network connection parameters.
                    self.is_connect = False
                    self.host = None
                    self.port = 8009

                    # Device and application configuration.
                    self.imgID = 0
                    self.inx = 0
                    self.start = None
                    self.det = None
                    self.model = model
                    self.user = user
                    self.fps = 30
                    self.edge_fps = edge_fps
                    self.device_fps= self.fps - self.edge_fps

                    # Simulation state.
                    self.iteration = iteration
                    self.flag = True
                    self.local = False
                    self.remote = False
                    self.send_controller = None


                    # Performance monitoring.
                    self.avg_pow = 0
                    self.avg_pow_Con = 0
                    self.avg_pow_hist = []
                    self.power_before_update=0
                    
                    # Execution timing.
                    self.time_l = []
                    self.time_r = []
                    
                    if self.device_fps < 0 :
                        self.device_fps = 0


                    # ---- Energy model parameters ----
                    self.Batt_info = {
                           "yolov5x.pt": 40920,
                           "yolov5l.pt": 21384,
                           "yolov5s.pt": 15400,
                           "yolov5m.pt": 30960
                    }
                    drone_flying_info={
                        "yolov5x.pt": 88.7,
                        "yolov5l.pt": 170,
                        "yolov5s.pt": 161.7,
                        "yolov5m.pt": 97.6
                    }
                    camera_trans_info={
                        "yolov5x.pt": 20,
                        "yolov5l.pt": 25,
                        "yolov5s.pt": 18,
                        "yolov5m.pt": 13
                    }

                    drone_info = {
                        "yolov5x.pt": 140,
                        "yolov5l.pt": 107,
                        "yolov5s.pt": 176,
                        "yolov5m.pt": 140
                    }


                    Batt_info = {
                        "yolov5x.pt": 40920,
                        "yolov5l.pt": 21384,
                        "yolov5s.pt": 15400,
                        "yolov5m.pt": 30960
                    }

                    # ---- Application execution and power models ----
                    app_info = {
                        "yolov5x.pt": 0.1792 * (self.device_fps) + 0.3923,
                        "yolov5l.pt": 0.6390 * (self.device_fps) + 1.274,
                        "yolov5s.pt": 0.2354 * (self.device_fps) + 0.3620,
                        "yolov5m.pt": 0.1202 * (self.device_fps) + 0.2280
                    }
                    pow_info = {
                        "yolov5x.pt": 179.3 * (self.device_fps) + 5930,
                        "yolov5l.pt": 362.8 * (self.device_fps) + 9830,
                        "yolov5s.pt": (402.8 * (self.device_fps) + 5294),
                        "yolov5m.pt": 169.1 * (self.device_fps) + 4918
                    }

                    # ---- Battery state and recorded histories ----
                    self.battry_level = Batt_info[self.model]
                    self.battry_level_real = Batt_info[self.model]

                    self.pow_hist = 0
                    self.power_consum_hist = 0
                    self.time_hist = []
                    self.remote_hist = []
                    self.power_consumption_history = []
                    self.TX2_energy_consumption_history = []
                    self.real_power_hist = []
                    self.real_battery_hist = []
                    self.battery_hist = []
                    self.delta1 = []
                    self.delta2 = []
                    self.Drone_long = 0

                    # Initial energy and power estimates before the iterative simulation begins.
                    self.power_information = ((((3000/app_info[self.model])*(pow_info[self.model] * app_info[self.model]*0.001)+(3000)+(drone_flying_info[self.model] * ( 6000))) / Batt_info[self.model]) * 100)/1000

                    self.power_consumption_information = ((3000/app_info[self.model])*(((pow_info[self.model]) * app_info[self.model]) / 1000)+(3000)+(drone_flying_info[self.model] * ( 6000)))/1000

                    self.Power_Consumption_TX2= ((3000/app_info[self.model])*(((pow_info[self.model]) * app_info[self.model]) / 1000))/1000
                    print(f"Execution time = {app_info[self.model]:.4f} ms")
                    print(f"Energy fraction = {self.power_information:.4f}")
                    print(f"Overall energy consumption = {self.power_consumption_information:.3f} mJ")
                    print(f"TX2 energy consumption = {self.Power_Consumption_TX2} mJ")

                    # Store communication messages and execution history.
                    self.message_information = []
                    self.time_sequence = []
                    self.TX2_fly = []
                    self.drone_fly = []
                    
                  
    def connect(self):
        """
        Initialize the device simulation, update its battery state,
        and run the first execution cycle.
        """
        self.start = time.time()
        self.batter_monitor()
        self.run()

    def batter_monitor(self):
        """
        Update the device parameters used for battery and energy estimation
        before executing the next simulation cycle.
        """
        self.device_fps = self.fps - self.edge_fps
        if self.device_fps < 0:
            self.device_fps = 0

    def Time_sequence(self):
        """
        Randomly select the drone operating mode for the current simulation cycle.
        """
        # Flying is weighted more heavily to represent the dominant activity
        # in the simulated drone timeline.  
        rand_list = [2, 3, 3, 3, 3, 3, 4]
        random_value = random.choice(rand_list)

        print(f"Selected operation mode = {random_value}")
        return random_value
    
    def run(self):
        """
        Execute one simulation cycle for the current device.

        The cycle updates the local and edge partition assignments, selects
        a drone operating mode, estimates energy consumption, executes the
        local and remote workloads, and updates the device battery state.
        """
        self.device_fps = self.fps - self.edge_fps

        if self.device_fps < 0:
            self.device_fps = 0

        print(f'device FPS = {self.device_fps}')
        # ---- Update partition assignment and energy-model parameters ----
        TX2_offset= {
            "yolov5x.pt": 0.3923 * 5930,
            "yolov5l.pt": 1.274 * 9830,
            "yolov5s.pt": 0.3620 * 5294,
            "yolov5m.pt":  0.2280 * 4918,
        }
        camera_trans_info = {
            "yolov5x.pt": 20,
            "yolov5l.pt": 25,
            "yolov5s.pt": 18,
            "yolov5m.pt": 13,
        }
        drone_flying_info = {
            "yolov5x.pt": 88.7,
            "yolov5l.pt": 170,
            "yolov5s.pt": 161.7,
            "yolov5m.pt": 97.6,
        }
        drone_info = {
            "yolov5x.pt": 140,
            "yolov5l.pt": 107,
            "yolov5s.pt": 176,
            "yolov5m.pt": 140,
        }

        app_info = {
            "yolov5x.pt": 0.1792 * (self.device_fps) + 0.3923,
            "yolov5l.pt": 0.6390 * (self.device_fps) + 1.274,
            "yolov5s.pt": 0.2354 * (self.device_fps) + 0.3620,
            "yolov5m.pt": 0.1202 * (self.device_fps) + 0.2280,

        }

        pow_info = {
            "yolov5x.pt": 179.3 * (self.device_fps) + 5930,
            "yolov5l.pt": 362.8 * (self.device_fps) + 9830,
            "yolov5s.pt": (402.8 * (self.device_fps) + 5294),
            "yolov5m.pt": 169.1 * (self.device_fps) + 4918,
        }

        # ---- Initialize energy usage and select the operating mode ----
        tx2_energy_usage = ((TX2_offset[self.model] * 0.001))
        print(f'TX2 energy consumption = {tx2_energy_usage}')
        self.Drone_long = self.Drone_long + app_info[self.model]
        print(f'Drone longevity = {self.Drone_long:.4f}')
 
        rand = self.Time_sequence()
        print(f'Device flag = {self.flag}')

        # ---- Compute energy consumption for the selected drone operating mode ----
        # ---- Model the drone activity timeline and energy consumption ----
        # The selected value represents the drone activity during the current
        # simulation interval. Each activity has a different duration and energy
        # consumption profile.
        if self.flag:
            # Mode 2: hover while transmitting camera data for six seconds.
            if rand == 2 and self.iteration:
                print("Operating mode: hovering")

                self.power_information = ((((camera_trans_info[self.model] * (3000)) + (drone_info[self.model] * (6000) + (1 * 3000))) / self.battry_level) * 100)/1000
                self.power_consumption_information = ((((camera_trans_info[self.model]) * (3000)) + (drone_info[self.model] * (6000))) + (1 * 3000))/1000
                print(f'Hovering power consumption ={self.power_consumption_information}')

                self.time_sequence.append("hovering(6s)")
                tx2_energy_usage = (3000+(camera_trans_info[self.model] * (3000)))/1000
                print(f"TX2 energy consumption during hovering = {tx2_energy_usage}")

            # Mode 3: fly and execute the assigned workload for five seconds.
            elif rand == 3 and self.iteration:
                print("Operating mode: flying")

                self.power_consumption_information = (((10000 / app_info[self.model]) * ((pow_info[self.model]) * (app_info[self.model]) * 0.001) + (drone_flying_info[self.model] * (10000))))/1000
                self.power_information = ((((10000 / app_info[self.model]) * ((pow_info[self.model]) * (app_info[self.model]) * 0.001) + (drone_flying_info[self.model] * (10000))) / self.battry_level) * 100)/1000
                print(f'Flying power consumption ={self.power_consumption_information}')

                tx2_energy_usage = ((5000 / app_info[self.model]) * ((pow_info[self.model]) * (app_info[self.model]) * 0.001))/1000
                print(f"TX2 energy consumption during flight = {tx2_energy_usage}")

                self.time_sequence.append("flying(5s)")
                self.TX2_fly.append(tx2_energy_usage)
                self.drone_fly.append(self.power_consumption_information)

            # Mode 4: hover without workload execution for five seconds.
            elif rand == 4 and self.iteration:
                print("Operating mode: hover only")

                self.power_information = (((((drone_info[self.model] + 1) * (5000))) / self.battry_level) * 100) / 1000
                self.power_consumption_information = (((drone_info[self.model] + 1) * 5000)) / 1000
                print(f'Hover-only power consumption  = {self.power_consumption_information}')

                self.time_sequence.append("only hover(5s)")
                tx2_energy_usage = (1 * 5000) / 1000
                print(f"TX2 energy consumption during hover-only mode = {tx2_energy_usage}")

        # ---- Low-battery return-to-station behavior ----
        #
        # Once the device enters the low-battery state, the drone stops normal
        # operation and flies back to the station for one second.
        if not self.flag:
            if self.iteration:
                print("Low-battery mode: returning to station")

                self.power_information = ((((drone_flying_info[self.model] * 1000) + (1000)) / self.battry_level) * 100)/1000

                self.power_consumption_information = ((drone_flying_info[self.model] * 1000) + (1000))/1000

                self.time_sequence.append("flying to the station(1s)")
                tx2_energy_usage = (1 * 1000) / 1000

        # Store the current cycle's power consumption for later analysis.
        self.power_consum_hist = self.power_consumption_information
        print(f'Power consumption history value = {self.power_consum_hist:.4f}')
        
        # ---- Execute local and edge workloads in parallel ----
        #
        # The local device workload and the edge-server workload are evaluated
        # concurrently, and their execution times are recorded for analysis.
        for i in range(1):
            start_t = time.time()

            items = [
                ("local", (self.device_fps)),
                ("remote", self.edge_fps)
            ]

            with ThreadPoolExecutor(2) as executor:
                results = executor.map(self.process, items)

            time_1, time_2 = results

            print(f"Server execution time = {time_2}")
            print(f"Device execution time = {time_1}")
            self.time_l.append(time_1)
            self.time_r.append(time_2)

            while time.time() - start_t <= 8:
                pass
            
            print(
            f"Partition {self.device_fps}/{self.edge_fps} completed in "
            f"{round(time_1 + time_2)} ms "
            f"(device={time_1}, server={time_2}), "
            f"power fraction = {self.power_information:.4f}, "
            f"power consumption = {self.power_consum_hist}"
            )
            print(f"Application execution time = {app_info[self.model]:.4f} ms")

            # Store the current cycle's power and timing statistics.
            self.avg_pow_Con = self.power_consum_hist
            self.avg_pow = (self.pow_hist)
            self.avg_pow_hist.append(self.avg_pow)
            self.power_consumption_information = self.avg_pow_Con

            # Record reported and real battery levels before applying the attack.
            self.battery_hist.append(self.battry_level)
            self.real_battery_hist.append(self.battry_level_real)

            print(f"Reported battery history = {self.battery_hist}")
            print(f"Real battery history = {self.real_battery_hist}")
            print(f"Current device ID = {self.user}")
        
            self.power_before_update = self.power_consumption_information

            # ---- Apply the data-falsification attack ----
            #
            # This implementation reproduces one experimental configuration used in
            # the paper. The compromised device ("Shima1") reports an inflated power
            # consumption by adding a uniformly distributed random offset between
            # 800 and 900. Other attack scenarios (different attack magnitudes and
            # multiple compromised devices) were evaluated separately in the paper.
            if self.user=="Shima1" and self.flag:
                if self.iteration :

                    rand1=(np.random.uniform(800, 900, 1)[0])
                    self.delta1.append(rand1)

                    print (f' Power consumption before attack = {self.power_before_update}')

                    self.power_consumption_information += rand1
                    self.power_information = ((self.power_consumption_information) / self.battry_level) * 100

                    print(f' Power consumption after attack = {self.power_consumption_information}')

            else:
                # For non-compromised devices, keep the original power-consumption value.
                self.power_consumption_information = self.power_before_update
                self.power_information = ((self.power_consumption_information) / self.battry_level) * 100

                print(f'Reported power consumption = {self.power_consumption_information}')

            # ---- Record power and energy histories for the current cycle ----
            self.power_consumption_history.append(self.power_consumption_information)
            self.TX2_energy_consumption_history.append(tx2_energy_usage)
            self.real_power_hist.append(self.power_before_update)
            
            print(f"Power fraction = {self.power_information:.3f}")
            if self.edge_fps == 30 and self.battry_level < 0:
                self.power_information = 0

            # ---- Update battery levels after the current simulation cycle ----
            if len(self.avg_pow_hist) > 0 and len(self.avg_pow_hist) % 10 == 0:
                print("Power history = {self.avg_pow_hist}")

            self.pow_hist = 0

            # The compromised device maintains both the reported battery level
            # and the real battery level for attack evaluation.
            if self.user == "Shima1" :

                    self.battry_level = self.battry_level - (self.power_consumption_information)
                    self.battry_level_real = self.battry_level_real - self.power_before_update
                    print(
                        f"Reported battery = {self.battry_level:.4f}, "
                        f"real battery = {self.battry_level_real:.4f}"
                    )
            else:
                self.battry_level= self.battry_level - (self.power_consumption_information)

            return(time_2 +time_1)

    def process(self, items):
        """
        Estimate execution time for either the local device workload
        or the edge-server workload.
        """
        p_type, fps = items

        app_info = {
            "yolov5x.pt": 0.1792 * (self.device_fps) + 0.3923,
            "yolov5l.pt": 0.6390 * (self.device_fps) + 1.274,
            "yolov5s.pt": 0.2354 * (self.device_fps) + 0.3620,
            "yolov5m.pt": 0.1202 * (self.device_fps) + 0.2280

        }
        server_app_info = {
            "yolov5x.pt": 0.06576*fps + 0.6831,
            "yolov5l.pt": 0.08880*fps + 0.1737,
            "yolov5s.pt": -0.07896*fps + 2.595,
            "yolov5m.pt": -0.1079*fps + 2.740
        }
        if p_type == "local":
            return round(app_info[self.model])
        

         
        if fps > 0:
            self.send_data(fps)

        return round(server_app_info[self.model])

    def send_data(self, fps):
            """
            Update the edge partition assignment and prepare the device message
            sent to the controller.
            """
            self.edge_fps = fps 
                

            data = "111111111111111111111111111111111"
          
            if len(self.time_r) > 0:
                self.message_information = {"data": data, "avg_pow": self.avg_pow, "user": self.user, "remote_r": (self.time_r[-1])}
               
            else:
                self.message_information = {"data": data, "avg_pow": self.avg_pow, "user": self.user,"remote_r":None}
                
            return()

     