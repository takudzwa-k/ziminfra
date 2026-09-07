from simulator import RoadSimulator
import json

sim = RoadSimulator("R001")
for i in range(5):
    print(json.dumps(sim.tick()))
