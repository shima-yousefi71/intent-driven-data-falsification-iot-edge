# Intent-driven Data Falsification Attack on Collaborative IoT-Edge Environments

This repository contains the implementation and experimental artifacts accompanying the paper:

> **Intent-driven Data Falsification Attack on Collaborative IoT-Edge Environments**

**Authors**

- Shima Yousefi
- Shameek Bhattacharjee
- Saptarshi Debroy

**Published in**

IEEE/ACM Symposium on Edge Computing (SEC), 2024

---

## Overview

Collaborative IoT-edge environments enable latency-sensitive AI applications by distributing computation between IoT devices and nearby edge servers. Since resource allocation decisions rely on the information reported by participating devices, compromised devices can manipulate the system by intentionally reporting falsified runtime information.

This repository implements the framework presented in our SEC 2024 paper for studying **intent-driven data falsification attacks** against collaborative IoT-edge environments. The framework evaluates how falsified energy reports influence task allocation, battery lifetime, and system behavior.

The evaluated attacker objectives include:

- Energy conservation (selfish intent)
- Battery depletion of non-compromised devices
- Deadline violation
- Operational impairment

---

## System Model

The simulated collaborative IoT-edge environment consists of:

- Camera-enabled drones
- NVIDIA Jetson TX2 devices
- Edge server
- Resource allocation controller
- Collaborative task offloading framework
- Battery and energy monitoring module

Each drone executes part of a DNN locally while offloading the remaining partitions to an edge server. During execution, devices periodically report their energy information to the controller, which dynamically updates the task allocation.

---

## Included Experimental Configuration

The current repository reproduces **one experimental scenario** from the paper.

Configuration:

- Four collaborative drone devices
- One compromised device (`Shima1`)
- 25% compromised devices
- Selfish attacker objective
- Falsified energy report sampled uniformly between **800 and 900**
- Dynamic edge resource allocation enabled
- Random drone operating modes (hovering, flying, return)

The current implementation corresponds to the **selfish intent attack** presented in the paper.

The paper additionally evaluates:

- Different attack intensities (Δ)
- Multiple compromised devices (50%)
- Model heterogeneity
- Drone heterogeneity
- Fully heterogeneous environments

These additional experimental configurations are not included in the current code release.

---

## Repository Structure

```text
.
├── code/
│   ├── devices.py
│   ├── Controller.py
│   ├── RootWidget.py
│   ├── networking.py
│   ├── random_devices.py
│   └── Remotrstage.py
│
├── experiments/
│
├── figures/
│
├── results/
│
└── README.md
```

### Directory Description

| Folder | Description |
|---------|-------------|
| **code/** | Source code for the collaborative IoT-edge simulator |
| **experiments/** | Experiment configurations |
| **figures/** | Figures presented in the paper |
| **results/** | Generated CSV and Excel output files |

---

## Running the Simulation

The main simulation entry point is:

```text
code/devices.py
```

Run the simulator from the repository root:

```bash
python code/devices.py
```

or

```bash
python3 code/devices.py
```

The simulator performs the following steps:

1. Creates four collaborative drone devices.
2. Assigns a YOLO model to each device.
3. Initializes battery capacity and edge partition allocation.
4. Simulates drone operation (hovering, flying, return).
5. Executes collaborative DNN inference.
6. Applies a selfish data falsification attack to the compromised device.
7. Updates the edge controller resource allocation.
8. Records battery level, power consumption, execution time, and attack statistics.

---

## Attack Configuration

The current implementation performs the attack on **Device 1 (`Shima1`)**.

The attack injects a falsified power consumption value sampled from

```text
Δ ~ Uniform(800,900)
```

during every attack iteration.

The attack implementation is located in:

```text
code/RootWidget.py
```

where the injected value is generated using

```python
rand1 = np.random.uniform(800, 900, 1)[0]
```

and applied only to

```python
if self.user == "Shima1" and self.flag:
```

Changing these values allows researchers to reproduce additional attack scenarios presented in the paper.

---

## Generated Results

Each simulation produces:

- Reported power consumption
- Actual power consumption
- Reported battery level
- Actual battery level
- TX2 energy consumption
- Drone operating timeline
- Injected attack values (Δ)
- Edge/server partition allocation

The generated CSV and Excel files are automatically stored inside the `results/` directory.

---

## Main Source Files

| File | Description |
|------|-------------|
| `devices.py` | Main simulation entry point |
| `Controller.py` | Dynamic edge resource allocation controller |
| `RootWidget.py` | Device simulation and attack implementation |
| `random_devices.py` | Device initialization |
| `Remotrstage.py` | Initial edge partition assignment |
| `networking.py` | Communication utilities |

---

## Paper

**Intent-driven Data Falsification Attack on Collaborative IoT-Edge Environments**

IEEE/ACM Symposium on Edge Computing (SEC), 2024

Paper:

https://ieeexplore.ieee.org/abstract/document/10818017

---

## Citation

If you use this repository in your research, please cite:

```bibtex
@inproceedings{yousefi2024intent,
  author    = {Shima Yousefi and Shameek Bhattacharjee and Saptarshi Debroy},
  title     = {Intent-driven Data Falsification Attack on Collaborative IoT-Edge Environments},
  booktitle = {IEEE/ACM Symposium on Edge Computing (SEC)},
  year      = {2024}
}
```

---

## License

This repository is released for academic and research purposes.

For commercial use or questions regarding the implementation, please contact the authors.