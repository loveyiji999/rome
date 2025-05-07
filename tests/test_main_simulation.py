# tests/test_main_simulation.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from core.car_state import CarState
from core.track_loader import load_track_segments
from core.turn_flow import TurnFlow

def test_five_turn_simulation():
    # 準備初始車輛與賽道資料
    car = CarState(schema_path="data/car_state_schema.yaml", limits_path="data/car_state_limits.yaml")
    segments = load_track_segments("data/track_config.yaml")
    flow = TurnFlow(car, segments, seed=1234)

    # 執行五回合模擬
    for _ in range(5):
        flow.simulate_turn()

    # 檢查 log 長度正確
    assert len(flow.log) == 5

    # 檢查每回合包含必要欄位
    for entry in flow.log:
        assert "turn" in entry
        assert "segment" in entry
        assert "event" in entry
        assert "pre_state" in entry
        assert "post_state" in entry

    # 至少有一回合觸發事件
    triggered = any(entry["event"] != "None" for entry in flow.log)
    assert triggered

    # 額外：印出所有回合摘要
    print("\n--- 五回合模擬事件摘要 ---")
    for entry in flow.log:
        print(f"第 {entry['turn']} 回合 - 切片：{entry['segment']} - 事件：{entry['event']}")
        print(f"  前：{entry['pre_state']}")
        print(f"  後：{entry['post_state']}\n")