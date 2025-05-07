# turn_flow.py

import random
from core.event_engine import load_events_from_folder

class TurnFlow:
    def __init__(self, car_state, segments, seed=None):
        self.car_state = car_state
        self.segments = segments
        self.current_turn = 0
        self.log = []
        self.seed = seed or random.randint(1000, 999999)
        self.random = random.Random(self.seed)

        # 只載入一次事件資料
        self.all_events = load_events_from_folder()

    def get_current_segment(self):
        index = self.current_turn % len(self.segments)
        return self.segments[index]

    def simulate_turn(self):
        self.current_turn += 1
        segment = self.get_current_segment()
        pre_state = self.car_state.summary()
        # 模擬上下文狀態
        context = {
            "distance_to_ai": 1.5,             # 假設目前與 AI 距離為 1.5m
            "slipstream_active": True,         # 正在尾流中
        }

        triggered_event = None

        # 嘗試觸發一個事件（每回合最多一件）
        for event in self.all_events:
            if event.is_triggered(segment, self.car_state, self.random, context):
                triggered_event = event
                event.apply_option("A", self.car_state)
            break

        post_state = self.car_state.summary()
        self.log.append({
            "turn": self.current_turn,
            "segment": segment.id,
            "segment_type": segment.track_type.value,
            "event": triggered_event.name if triggered_event else "None",
            "option": "A" if triggered_event else None,
            "pre_state": pre_state,
            "post_state": post_state,
        })

    def print_log(self):
        for entry in self.log:
            print(f"【第 {entry['turn']} 回合】{entry['segment_type']} → 事件：{entry['event']}")
            print(f"  前：{entry['pre_state']}")
            print(f"  後：{entry['post_state']}\n")
