# Intent-driven Data Falsification Attack on Collaborative IoT-Edge Environments

This repository contains code and experimental artifacts related to the paper:

**Intent-driven Data Falsification Attack on Collaborative IoT-Edge Environments**

Shima Yousefi, Shameek Bhattacharjee, Saptarshi Debroy  
IEEE/ACM Symposium on Edge Computing (SEC), 2024

## Overview

Collaborative IoT-edge environments are widely used for hosting latency-sensitive AI applications. However, these systems are vulnerable to **data falsification attacks**, where compromised IoT devices misreport system parameters to manipulate resource allocation decisions.

This project investigates **intent-driven data falsification attacks** that target key system objectives such as:

- Energy efficiency
- Application latency
- System stability

## Attack Intents Studied

The paper studies four attacker intents:

1. Save energy (selfish intent)
2. Drain non-compromised devices
3. Jeopardize task deadlines
4. Operational impairment

## System Model

The experiments simulate a collaborative IoT-edge environment consisting of:

- camera-enabled drones
- edge server controller
- task offloading framework
- energy monitoring and reporting

## Experimental Setup

The attack model is evaluated using **testbed-in-the-loop simulations** involving:

- NVIDIA Jetson TX2 devices as IoT nodes
- Edge server controller
- simulated drone energy models

## Repository Structure

