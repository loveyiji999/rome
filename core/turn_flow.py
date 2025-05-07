import random
from core.logic_rules import apply_logic_rules

class TurnFlow:
    def __init__(self, car_state, segments, seed=None, events=None):
        self.car_state = car_state
        self.segments = segments
        self.current_turn = 0
        self.log = []
        self.seed = seed or random.randint(1000, 999999)
        self.random = random.Random(self.seed)
        self.all_events = events or []

    def get_current_segment(self):
        index = self.current_turn % len(self.segments)
        return self.segments[index]

    def simulate_turn(self):
        self.current_turn += 1
        segment = self.get_current_segment()
        pre_state = self.car_state.summary()

        context = {
            "fuel": self.car_state.get("fuel_module.fuel"),
            "tire_wear": self.car_state.get("tire_module.tire_wear"),
            "distance_to_ai": 1.5,
            "slipstream_active": True,
            "laps_completed": self.car_state.get("race_info_module.laps_completed")
        }

        triggered_event = None
        triggered_name = "None"
        candidates = []
        triggered_mutex = set()

        for event in self.all_events:
            # 排除已觸發 mutex 組別
            if event.mutex and event.mutex in triggered_mutex:
                continue

            if event.is_triggered(segment, self.car_state, self.random, context):
                candidates.append(event.name)
                if not triggered_event:
                    triggered_event = event
                    triggered_name = event.name
                    event.apply_option("A", self.car_state)
                    event.cooldown_remaining = event.cooldown
                    if event.mutex:
                        triggered_mutex.add(event.mutex)

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

        for event in self.all_events:
            if event.cooldown_remaining > 0:
                event.cooldown_remaining -= 1

        apply_logic_rules(self.car_state)

    def print_log(self):
        print("\n===== 回合事件紀錄 =====")
        for entry in self.log:
            print(f"【第 {entry['turn']} 回合】{entry['segment_type']} → 事件：{entry['event']}")
            print(f"  前：{entry['pre_state']}")
            print(f"  後：{entry['post_state']}\n")