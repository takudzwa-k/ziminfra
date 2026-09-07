"""
Shared configuration for the Road IoT Simulator.
"""

# Road segments being simulated.
ROADS = [
    {"road_id": "R001", "name": "Samora Machel Ave (CBD)"},
    {"road_id": "R002", "name": "Enterprise Rd (Borrowdale)"},
    {"road_id": "R003", "name": "Simon Mazorodze Rd (Southerton)"},
]

# MQTT broker settings
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_TEMPLATE = "roads/{road_id}/data"

# How often (seconds) each road publishes a combined reading
PUBLISH_INTERVAL_SECONDS = 5

# Random seed for reproducible demo runs (set to None for true randomness)
RANDOM_SEED = None