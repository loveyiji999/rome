import yaml
from pathlib import Path
from core.condition_parser import evaluate_condition
import random
class Event:
    def __init__(self, data):
        self.id = data["id"]
        self.category = data["category"]
        self.name = data["name"]
        self.description = data["description"]
        self.trigger = data.get("trigger", {})
        self.options = data.get("options", [])
        self.cooldown = data.get("cooldown", 0)
        self.cooldown_remaining = 0
        self.mutex = data.get("mutex")
        # 嚴重度分級 (可選): low, medium, high
        self.severity = data.get("severity", "medium")
        # 事件優先級，數字越大代表越優先
        self.priority = data.get("priority", 0)
        # 是否為獨佔事件，獨佔事件一旦觸發，當回合只執行此事件
        self.solo = data.get("solo", False)
        # 自訂該事件可與同類事件在同一區段堆疊的數量上限
        self.max_per_segment = data.get("max_per_segment")

    def is_triggered(self, segment, car_state, random_obj, context):
        # 冷卻中不可觸發
        if self.cooldown_remaining > 0:
            return False
        # 區段篩選
        if segment.track_type.value not in self.trigger.get("segment_type", []):
            return False
        # 條件判斷
        for cond in self.trigger.get("conditions", []):
            if not evaluate_condition(cond, car_state, context):
                return False
        # 計算觸發機率 (含動態加成)
        base_prob = self.trigger.get("probability", 0.0)
        total_prob = base_prob
        for dp in self.trigger.get("dynamic_probability", []):
            # dp 範例: {name: ..., params: {...}, bonus: 0.2}
            cond_def = {"name": dp.get("name"), "params": dp.get("params", {})}
            if evaluate_condition(cond_def, car_state, context):
                total_prob += dp.get("bonus", 0)
        # 上限 1.0
        total_prob = min(total_prob, 1.0)
        # 隨機判定
        return random_obj.random() < total_prob

    def apply_option(self, option_key, car_state):
        for opt in self.options:
            if opt["key"] == option_key:
                for effect in opt.get("consequences", []):
                    target = effect.get("target")
                    delta = effect.get("delta", {})
                    for method, value in delta.items():
                        car_state.apply_change(target, method, value)
                feedback_pool = opt.get("feedback", [])
                return random.choice(feedback_pool) if feedback_pool else None
        raise ValueError(f"選項 {option_key} 不存在於事件 {self.id}")

    def get_option_keys(self):
        return [opt.get("key") for opt in self.options]


def load_events_from_folder(folder_path="events"):
    events = []
    for filename in Path(folder_path).glob("*.yaml"):
        with open(filename, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
            for data in raw:
                events.append(Event(data))
    # 根據 severity 與 priority 排序: high > medium > low，再依 priority 倒序
    severity_order = {"high": 0, "medium": 1, "low": 2}
    events.sort(key=lambda e: (severity_order.get(e.severity, 1), -e.priority))
    return events
