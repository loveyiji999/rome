import random
from core.event_engine import load_events_from_folder

class TurnFlow:
    def __init__(self, car_state, segments, seed=None, events=None):
        self.car_state = car_state
        self.segments = segments
        self.current_turn = 0
        self.log = []
        self.seed = seed or random.randint(1000, 999999)
        self.random = random.Random(self.seed)
        self.all_events = events or load_events_from_folder("data/events")

    def get_current_segment(self):
        index = self.current_turn % len(self.segments)
        return self.segments[index]

    def simulate_turn(self):
        self.current_turn += 1
        segment = self.get_current_segment()
        pre_state = self.car_state.summary()

        # 模擬 context：每種條件都滿足一點
        context = {
            "fuel": self.car_state.get("fuel_module.fuel"),
            "tire_wear": self.car_state.get("tire_module.tire_wear"),
            "distance_to_ai": 1.5,
            "slipstream_active": True,
            "laps_completed": 10
        }

        triggered_event = None
        triggered_name = "None"
        candidates = []

        for event in self.all_events:
            if event.is_triggered(segment, self.car_state, self.random, context):
                candidates.append(event.name)
                if not triggered_event:
                    triggered_event = event
                    event.apply_option("A", self.car_state)
                    triggered_name = event.name

        post_state = self.car_state.summary()
        self.log.append({
            "turn": self.current_turn,
            "segment": segment.id,
            "segment_type": segment.track_type.value,
            "event": triggered_name,
            "option": "A" if triggered_event else None,
            "pre_state": pre_state,
            "post_state": post_state
        })

        print(f"第 {self.current_turn} 回合 - 區段：{segment.track_type.value} - 可觸發事件：{candidates}")
        if triggered_event:
            print(f"→ 實際觸發事件：{triggered_event.name}")

    def print_log(self):
        print("\n===== 回合事件紀錄 =====")
        for entry in self.log:
            print(f"【第 {entry['turn']} 回合】{entry['segment_type']} → 事件：{entry['event']}")
            print(f"  前：{entry['pre_state']}")
            print(f"  後：{entry['post_state']}\n")