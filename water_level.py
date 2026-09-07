from sensors import WaterLevelSensor
s = WaterLevelSensor("R001")
print(s.read(rainfall_mm_h=50))
