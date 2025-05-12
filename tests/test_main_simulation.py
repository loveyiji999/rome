# test_main_simulation.py
import sys
import os
import argparse

# 將專案根目錄加入搜尋路徑，才能正確匯入 core、data 等模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.car_state import CarState
from core.track_loader import load_track_segments
from core.turn_flow import TurnFlow
from core.event_engine import load_events_from_folder

def main(turns: int = 20):
    """
    執行模擬主流程
    :param turns: 模擬回合數
    """
    # 初始化車輛與賽道資料
    car = CarState(
        schema_path="data/car_state_schema.yaml",
        limits_path="data/car_state_limits.yaml"
    )
    segments = load_track_segments("data/track_config.yaml")
    events = load_events_from_folder("data/events")  # 載入所有事件 YAML

    # 初始化回合流程控制
    flow = TurnFlow(car, segments, seed=2025, events=events)

    # 模擬指定回合數
    for _ in range(turns):
        flow.simulate_turn()

    # 輸出結果
    flow.print_log()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="測試遊戲主流程模擬",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-t", "--turns",
        type=int,
        default=20,
        help="要模擬的回合數"
    )
    args = parser.parse_args()
    main(turns=args.turns)
