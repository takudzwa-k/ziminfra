# Road IoT Simulator 🚧📡

## 📖 Description

A Python simulation of smart road infrastructure sensors — rainfall, drainage, road vibration, traffic, and temperature. 
This simulates what real physical sensors embedded in a road would report, without needing any actual hardware.

---

## ✨ Features

- Simulates 5 types of road sensors, each with realistic behavior.
- Simulates multiple road segments at once, each with independent sensors.
- Detects **infrastructure events** automatically — blocked drains, heavy rainfall, rising road vibration, and road deterioration — based on the sensor readings, the same way a real monitoring system would
- Displays a **live dashboard** in the terminal so you can watch sensor readings update in real time.
- Designed to plug into MQTT for publishing data to other systems 

---

## 🗂 Project Structure


```
road-iot-sim/
├── run_simulation.py       # Main entry point — run this to start the simulation
├── simulator.py            # Combines all sensors + event detection per road
├── config.py                # Settings: which roads exist, timing, MQTT config
│
├── sensors/                  # One file per simulated sensor
│   ├── __init__.py
│   ├── base.py               # Shared base class all sensors inherit from
│   ├── rainfall.py           # Rainfall sensor (mm/hour)
│   ├── water_level.py        # Drain / water-level sensor (cm)
│   ├── vibration.py          # Road vibration / accelerometer sensor (g)
│   ├── traffic.py            # Traffic counter sensor (vehicles/hour)
│   └── temperature.py        # Temperature sensor (°C)
│
└── scenarios/                 # Infrastructure event logic & scripted demos
    ├── __init__.py
    ├── events.py               # Detects events from sensor readings (rules engine)
    └── scripted_scenarios.py   # Predefined event timelines for demos
```

---

## 🔗 How it all fits together

```
 ┌─────────────┐   ┌──────────────┐   ┌─────────────┐   ┌───────────┐   ┌─────────────┐
 │  Rainfall   │──▶│ Water Level  │   │  Vibration  │◀──│  Traffic  │   │ Temperature │
 └─────────────┘   └──────────────┘   └─────────────┘   └───────────┘   └─────────────┘
        │                  │                 │                 │               │
        └──────────────────┴─────────────────┴─────────────────┴───────────────┘
                                         │
                                 ┌───────▼────────┐
                                 │  RoadSimulator  │   (simulator.py)
                                 │ combines all 5  │
                                 │ sensor readings │
                                 └───────┬────────┘
                                         │
                                 ┌───────▼────────┐
                                 │ Event Detection │   (scenarios/events.py)
                                 │  (blocked drain,│
                                 │  heavy rain...) │
                                 └───────┬────────┘
                                         │
                                 ┌───────▼────────┐
                                 │ run_simulation  │   (run_simulation.py)
                                 │  live dashboard │
                                 └────────────────┘
```

## 📋 Requirements 

- Python 3.10 or newer (uses modern type hints like `dict | None`)
- The [`rich`](https://github.com/Textualize/rich) library, for the live
  terminal dashboard

Install the one dependency:

```bash
pip install rich --break-system-packages
```

> If you're not on a system that requires `--break-system-packages`, just
> run `pip install rich`.

---


## ⚡ Installation

1. Clone or download this repository.
2. Open a terminal and navigate into the project folder (the one containing
   `run_simulation.py`):
   ```bash
   cd road-iot-sim
   ```
3. Install the dependency (see above).
4. Run the simulator:
   ```bash
   python3 run_simulation.py
   ```
5. You'll see a live-updating table like this, refreshing every few seconds:

   ```

## 🚀  Configuring the simulation

All the settings you're likely to want to change live in `config.py`:

```python
ROADS = [
    {"road_id": "R001", "name": "Samora Machel Ave (CBD)"},
    {"road_id": "R002", "name": "Enterprise Rd (Borrowdale)"},
    {"road_id": "R003", "name": "Simon Mazorodze Rd (Southerton)"},
]

PUBLISH_INTERVAL_SECONDS = 5   # how often readings update
```

Add more roads by adding more entries to `ROADS` — no other code changes
needed.

---

## 🚨 Sensor details

| Sensor | File | Unit | Behavior |
|---|---|---|---|
| Rainfall | `sensors/rainfall.py` | mm/hour | Mostly dry, occasional realistic rain bursts using a gamma distribution |
| Water level | `sensors/water_level.py` | cm | Rises with rainfall, drains slowly over time (or barely at all if "blocked") |
| Vibration | `sensors/vibration.py` | g (accelerometer units) | Scales with traffic volume; can permanently worsen to simulate road damage |
| Traffic | `sensors/traffic.py` | vehicles/hour | Follows a realistic rush-hour pattern (peaks ~8am and ~5pm) |
| Temperature | `sensors/temperature.py` | °C | Follows a daily heating/cooling cycle |

---

## ⛈️ Infrastructure events

The system automatically detects these conditions from the sensor data
(see `scenarios/events.py`):

| Event | Trigger condition |
|---|---|
| `heavy_rainfall` | Rainfall ≥ 40 mm/h |
| `blocked_drain` | Water level ≥ 70 cm while rainfall is low (drain isn't clearing) |
| `increasing_road_vibration` | Vibration has been steadily rising over the last 5 readings |
| `road_deterioration` | Vibration is very high and sustained |

Scripted demo scenarios (`scenarios/scripted_scenarios.py`) can also force
these events on at specific times, useful for demos and testing without
waiting for random conditions to occur naturally.

---