from core.car_state import CarState
from core.track_loader import load_track_segments
from core.turn_flow import TurnFlow

car = CarState()
segments = load_track_segments("track_config.yaml")
flow = TurnFlow(car, segments, seed=2025)

for _ in range(100):
    flow.simulate_turn()

flow.print_log()
