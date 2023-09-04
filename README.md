# IoT_Parkinson_Project_v2
Course project for Programming for IoT Applications

## Info
### University
Politecnico di Torino

### Course
Master of Science program in ICT for Smart Societies

01QWRBH - Programming for IoT applications

## Getting started
Parkinson Pal is a system created to help patients with Parkinson desase. The enviroment set on this repository includes the necessary tools to register new patients on the system, simulate their sensors and actuators, and process the information exchanged by them.

### Tools
- Python 3.6 or higher

### Run the system
#### Catalog

```
cd catalog
py catalog_Manager.py
```

#### Patients simulation

Script for patient 1 registration:

```
cd Simulated_Patients/Patient1
py Patient1_Simulator.py
```

Scripts for patient 1 actuators simulations:

```
py DBS1_Simulator.py
py SoundFeedback1_Simulator.py
```

### Microservices

Run all the scripts on Microservices

```
cd Microservices
py fall_management.py
py freezing_management.py
py tremor_management.py
py statistics_management.py
```

#### Telegram bot server

```
cd telegram-bot
py bot.py
```

#### Thingspeak adaptor

```
cd Thingspeak
py Thingspeak_adaptor_v2.py
```

## Team
- Marta Bono
- Francesco Calice
- Luca Barotto
- Candela Muzás 