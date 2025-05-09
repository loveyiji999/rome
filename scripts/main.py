# scripts/main.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.car_state import CarState
from core.track_loader import load_track_segments
from core.turn_flow import TurnFlow
from core.event_engine import load_events_from_folder
from core.map_loader import load_track_map

def main(turns=20):
    # 初始化車輛與賽道段資料
    car = CarState(schema_path="data/car_state_schema.yaml", limits_path="data/car_state_limits.yaml")
    all_segments = load_track_segments("data/track_config.yaml")
    
    # 地圖讀取與拼接
    map_info, track = load_track_map("data/maps/format F1 Sim V1.yaml", all_segments)

    # 載入事件
    events = load_events_from_folder("data/events")

    # 初始化流程模組
    flow = TurnFlow(car, track, seed=2025, events=events)

    # 模擬
    for _ in range(turns):
        flow.simulate_turn()

    # 輸出紀錄
    flow.print_log()

if __name__ == "__main__":
    main(turns=20)