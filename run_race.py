# run_race.py
import argparse
from core.car_state import CarState
from core.track_loader import load_track_segments
from core.event_engine import load_events_from_folder
from core.race import Race

def main(laps):
    # 1. 初始化車輛
    player = CarState(schema_path="data/car_state_schema.yaml", limits_path="data/car_state_limits.yaml")
    player.name = "Player"
    ai1 = CarState(schema_path="data/car_state_schema.yaml", limits_path="data/car_state_limits.yaml")
    ai1.name = "AI Racer 1"
    ai2 = CarState(schema_path="data/car_state_schema.yaml", limits_path="data/car_state_limits.yaml")
    ai2.name = "AI Racer 2"

    # 2. 載入賽道與事件
    segments = load_track_segments("data/track_config.yaml")   # 賽道設定檔路徑 :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
    events = load_events_from_folder("data/events")            # 事件資料夾 :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}

    # 3. 建立並執行 Race
    race = Race([player, ai1, ai2], segments, events, seed=66666)
    race.run(laps)

    # 4. 列印最終排名
    race.print_standings()

    # 5. 顯示玩家的詳細回合日誌
    print("\n===== 玩家回合詳情 =====")
    for entry in race.flows[0].log:
        print(f"回合 {entry['turn']:2d} | 區段 {entry['segment_type']:15s} | 事件: {entry['event']:<25s} | 用時: {entry['time']:.2f}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--laps", type=int, default=3, help="模擬圈數")
    args = parser.parse_args()
    main(args.laps)
