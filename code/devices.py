"""
devices.py

Main simulation script for the collaborative IoT-edge experiment.

This file:
- creates devices and controllers
- initializes the simulation environment
- runs the iterative experiment
- collects device energy and timing information
- exports the experiment results
"""

from pathlib import Path
import pandas as pd
import random
from RootWidget import RootWidget
from random_devices import generate_device_parameters
from Controller import Controller

#-------------------------
# Experiment configuration
#-------------------------
RANDOM_SEED = 10
DEVICE_TOTAL = 4
TOTAL_PARTITIONS = 30
MAX_ITERATIONS = 5
ID_LENGTH = 13
RESULTS_DIR = Path("results")


random.seed(RANDOM_SEED)
iteration = None
device_total = DEVICE_TOTAL
id_len = ID_LENGTH

model_type_list, device_id_list, edge_fps = generate_device_parameters(id_len, device_total)
second_time = [False] * device_total
first = [False] * device_total
flag = [True] * device_total
sum_edge_fps = []
k = 0 # index used to track each device in device_list and devices_information
device_list = []  # store all created device objects
URB_to_device = []
devices_information = [
    {'power': None, 'power consumption': None, 'time': None, 'battery': None}
    for i in range(device_total)
    ]  # store per-device simulation data

battery_capacity = []

for model_type, device_id, edge_device_fps in zip(model_type_list, device_id_list, edge_fps):
    if k < device_total:
        # ---- Device configuration info ----
        print(
            f"Device {k}: model = {model_type} || "
            f"device_ID = {device_id} || "
            f"total_partitions = {TOTAL_PARTITIONS} || "
            f"server_partition(min) = {edge_device_fps} || "
            f"device_partitions(max) = {TOTAL_PARTITIONS - edge_device_fps}"
            )
        print("#" * 100)
        # ---- Create and connect device ----
        widget = RootWidget(model_type, device_id, edge_device_fps, iteration)  # create one device object for this simulation
        widget.connect()
        # ---- Store device metrics ----
        devices_information[k]['power'] = widget.power_information  # fraction of power is stored in dictionary
        devices_information[k]['power consumption'] = widget.power_consumption_information  # power consumption is stored in dictionary
        device_list.append(widget)
        # ---- Store battery information ----
        batt = widget.Batt_info[model_type] - ((widget.power_consumption_information))
        print(f"Initial battery capacity = {widget.Batt_info[model_type]}")

        battery_capacity.append(widget.Batt_info[model_type])
        print(f"Initial power consumption = {widget.power_consumption_information:.4f}")
        
        # ---- Create controller for this device ----
        URB = Controller(model_type, device_id, edge_device_fps, device_total)
        URB_to_device.append(URB)
        sum_edge_fps.append(edge_device_fps) # track minimum server stages assigned to this device
        print(f"Initial power fraction = {devices_information[k]['power']:.4f}")
        k = k + 1

used_fps = sum(sum_edge_fps)
print(f'used capacity of server={used_fps}')
print("battery_capacity = ", battery_capacity)
power_list = []
power_consumption_list = []

new_edge_fps = [None for i in range(device_total)]
message = [{"data": None, "avg_pow": None, "user": None, "remote_r": None} for l in range(device_total)]
iteration = 0
i = 0
# -------------------------------------------------------------------------
# Initial server allocation
#
# Before the iterative simulation begins, collect the initial power reports
# from all devices and let the controller compute the first edge allocation.
# -------------------------------------------------------------------------
for k in range(device_total):
    print(f"Device {k} :")
    device = device_list[k]
    print(f"device_power = {device.power_information}")
    print(f"power_consumption = {device.power_consumption_information}")
    power_list.append(devices_information[k]['power'])
    power_consumption_list.append(devices_information[k]['power consumption'])
print(f'power fraction list(0)= {power_list}')
print(f'power consumption list (0)= {power_consumption_list}')
total_power_consumption = sum(power_list)
print(f'total_power_fractions = {total_power_consumption}')

for d in range(device_total):
    device = device_list[d]
    urbdevice = URB_to_device[d]
    urbdevice.urb_to_device(used_fps, device_total)
    device.edge_fps = (
        urbdevice.new_fps(
            iteration,
            power_list[d], 
            total_power_consumption,
            power_consumption_list[d], 
            batt)
            + sum_edge_fps[d]
    )
    print(f"initial edge_fps for device {d} = {device.edge_fps}")
remote_time = []

for iteration in range(1, MAX_ITERATIONS):
    print(f"Iteration = {iteration}")

    power_list = [0 for i in range(device_total)]
    power_consumption_list = [0 for i in range(device_total)]
    battery_list = [0 for i in range(device_total)]
    for m in range(device_total):
        if not device_list[m].edge_fps and first[m]:
            redundant_rand = device_list[m].Time_sequence()
            continue
        device = device_list[m]
        device_info = devices_information[m]
        device.iteration = True
        device_info['time'] = device.run()
        device_info['power'] = device.power_information
        device_info['power consumption'] = device.power_consumption_information
        device_info['battery'] = device.battry_level

        power_list[m] = device_info['power']
        battery_list[m] = device_info['battery']

        # When a device reaches 20% of its initial battery capacity,
        # the controller shifts more computation toward the edge server.
        if flag[m] and (battery_list[m] < 0.2 * battery_capacity[m]):
            used_fps = used_fps + (TOTAL_PARTITIONS - sum_edge_fps[m])  # if one device is drained, server should allocate more stage to the task of that device
            flag[m] = False
            device.flag = flag[m]
            used_fps1 = used_fps
            # If the remaining server capacity is no longer sufficient to support
            # the affected devices, the system transitions to the jeopardized-deadline case.
            if used_fps > 72:
                for j in range(device_total):
                    second_time[j] = True
                    used_fps = 0  # added after I decide to consider jeopardized devise. previously it was the above line
                    sum_edge_fps = [0] * device_total
                    print('Deadline is Jeopardized')
        if battery_list[m] < 0 :
            used_fps = 0  # added after I decide to consider jeopardized devise. previously it was the above line
            sum_edge_fps = [0] * device_total
            first[m] = True
            used_fps = sum(sum_edge_fps)

        if (battery_list[m] < (0.08 * battery_capacity[m])) and (second_time[m] == False):
            power_list[m] = 0
        if first[m]:
            device_total = device_total - 1
            
        power_consumption_list[m] = devices_information[m]['power consumption']
        message[m] = device.message_information
        
        print(f'power fraction list {m + 1} = {power_list}')
        print(f'power consumption list {m + 1} = {power_consumption_list}')
    total_power_consumption = sum(power_list)
    print(f'Updated device information = {devices_information}')

# -------------------------------------------------------------------------
# Update server allocation
#
# After receiving the latest device reports, the controller recomputes how
# many stages should be executed at the edge for each active device.
# -------------------------------------------------------------------------

    for m in range(device_total):
        device = device_list[m]

        if device.battry_level:
            urbdevice = URB_to_device[m]
            print(f' urbdevice.remain_edge_fps = {urbdevice.remain_edge_fps}')

            if not device.edge_fps:
                continue

            if second_time[m]:
                used_fps = 0

            urbdevice.urb_to_device(used_fps, device_total)
            server_fps = urbdevice.new_fps(iteration, power_list[m], total_power_consumption, power_consumption_list[m],
                                           battery_list[m])
            
            print("server_fps from controller = ", server_fps)
            print("second_time[m]", second_time[m])

            if power_list[m] == 0 and not second_time[m]:
                server_fps = TOTAL_PARTITIONS
                print(f"server_fps set to maximum = {server_fps}")

            if server_fps or server_fps == 0:
                if server_fps == TOTAL_PARTITIONS or server_fps + sum_edge_fps[m] > TOTAL_PARTITIONS:
                    device.edge_fps = TOTAL_PARTITIONS
                else:
                    device.edge_fps = server_fps + sum_edge_fps[m]
                    print(f"Updated edge_fps = {device.edge_fps}, server_fps = {server_fps}, base_edge_fps = {sum_edge_fps[m]}")


            else:
                device.edge_fps = TOTAL_PARTITIONS
                print(f' Device{m + 1} is drained')
                i += 1

            print("server fps =", server_fps)

            if first[m] and battery_list[m] < 0:
                device.edge_fps = 0
                
        else:
            device.edge_fps = 0
            print(f' Device{m + 1} is drained')

            i += 1

# -------------------------------------------------------------------------
# Export simulation results
#
# After the simulation completes, each device's recorded histories are
# converted into DataFrames and saved for post-processing, visualization,
# and statistical analysis.
# -------------------------------------------------------------------------           
print("Simulation finished. Starting result export...")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
print(f"Saving results to: {RESULTS_DIR.resolve()}")
for m in range(device_total):
    # Collect recorded histories for the current device.
    power_history = device_list[m].power_consumption_history
    real_power_history = device_list[m].real_power_hist
    tx2_power_history = device_list[m].TX2_energy_consumption_history
    battery_history = device_list[m].battery_hist
    real_battery_history = device_list[m].real_battery_hist
    operation_mode = device_list[m].time_sequence
    drone_flight_history = device_list[m].drone_fly
    tx2_flight_history = device_list[m].TX2_fly
    delta_history_1 = device_list[m].delta1
    delta_history_2 = device_list[m].delta2
    # Convert recorded histories into pandas DataFrames.
    power_df = pd.DataFrame(data=power_history, columns=[''])
    real_power_df = pd.DataFrame(data=real_power_history, columns=[''])
    tx2_power_df = pd.DataFrame(data=tx2_power_history, columns=[''])
    battery_df = pd.DataFrame(data=battery_history, columns=[''])
    real_battery_df = pd.DataFrame(data=real_battery_history, columns=[''])
    sequence_df = pd.DataFrame(data=operation_mode, columns=[''])
    DroneFlyFrame = pd.DataFrame(data=drone_flight_history, columns=[''])
    Tx2FlyFrame = pd.DataFrame(data=tx2_flight_history, columns=[''])
    delta_1_df = pd.DataFrame(data=delta_history_1,columns=[''])
    delta_2_df = pd.DataFrame(data=delta_history_2, columns=[''])

    # Export results in CSV format for plotting and automated post-processing.
    power_df.to_csv(RESULTS_DIR / f"powerDataFrame_D{m + 1}.csv")
    real_power_df.to_csv(RESULTS_DIR / f"Realpower_D{m + 1}.csv")
    battery_df.to_csv(RESULTS_DIR / f"BatteryDataFrame_D{m + 1}.csv")
    real_battery_df.to_csv(RESULTS_DIR / f"Real_Battery_D{m + 1}.csv")
    tx2_power_df.to_csv(RESULTS_DIR / f"TX2Power{m + 1}.csv")
    sequence_df.to_csv(RESULTS_DIR / f"timeline{m + 1}.csv")

    # Export results in Excel format for manual inspection and reporting.
    power_df.to_excel(RESULTS_DIR / f"powerDataFrameExcel2_D{m + 1}.xlsx")
    real_power_df.to_excel(RESULTS_DIR / f"Realpower_D{m + 1}.xlsx")
    battery_df.to_excel(RESULTS_DIR / f"BatteryDataFrameExcel2_D{m + 1}.xlsx")
    real_battery_df.to_excel(RESULTS_DIR / f"Real_Battery_Excel_D{m + 1}.xlsx")
    tx2_power_df.to_excel(RESULTS_DIR / f"TX2Power{m + 1}.xlsx")
    sequence_df.to_excel(RESULTS_DIR / f"timeline{m + 1}.xlsx")
    if delta_history_1:
        delta_1_df.to_excel(
            RESULTS_DIR / f"Delta1_D{m + 1}.xlsx",
            index=False,
        )

    if delta_history_2:
        delta_2_df.to_excel(
            RESULTS_DIR / f"Delta2_D{m + 1}.xlsx",
            index=False,
        )
