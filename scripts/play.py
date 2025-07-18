# scripts/play.py
import sys
import os

# Add project root to sys.path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.car_state import CarState
from core.track_loader import load_track_segments
from core.turn_flow import TurnFlow
from core.event_engine import load_events_from_folder
from core.map_loader import load_track_map


def main():
    # Ask user for number of turns (default 20)
    try:
        turns_input = input("請輸入比賽回合數（預設為20）: ").strip()
        turns = int(turns_input) if turns_input else 20
    except ValueError:
        turns = 20

    # Initialize car state
    car = CarState(schema_path="data/car_state_schema.yaml",
                   limits_path="data/car_state_limits.yaml")

    # Load track segments and map
    all_segments = load_track_segments("data/track_config.yaml")
    _, track = load_track_map("data/maps/format F1 Sim v1.yaml", all_segments)

    # Load events
    events = load_events_from_folder("data/events")

    # Create turn flow with player control
    flow = TurnFlow(car_state=car, seed=2025, events=events, is_player=True)

    # Run simulation
    for _ in range(turns):
        flow.simulate_turn(track)

    # Print final log and summary
    if hasattr(flow, "print_log"):
        flow.print_log()
    else:
        # fall back: print all log entries
        for entry in flow.log:
            print(entry)

    print("比賽結束！最終車車狀態：")
    print(car.summary())


if __name__ == "__main__":
    main()
