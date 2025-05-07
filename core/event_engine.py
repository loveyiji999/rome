import yaml
from pathlib import Path
class Event:
    def __init__(self, data):
        self.id = data["id"]
        self.category = data["category"]
        self.name = data["name"]
        self.description = data["description"]
        self.trigger = data["trigger"]
        self.options = data["options"]
        self.cooldown = data.get("cooldown", 0)
        self.cooldown_remaining = 0

    def is_triggered(self, segment, car_state, random_obj, context):
        if self.cooldown_remaining > 0:
            return False

        if segment.track_type.value not in self.trigger.get("segment_type", []):
            return False

        for cond in self.trigger.get("conditions", []):
            if not evaluate_condition(cond, car_state, context):
                return False

        prob = self.trigger.get("probability", 0.0)
        return random_obj.random() < prob

    def apply_option(self, option_key, car_state):
        for opt in self.options:
            if opt["key"] == option_key:
                for effect in opt["consequences"]:
                    target = effect["target"]
                    delta = effect["delta"]
                    for method, value in delta.items():
                        car_state.apply_change(target, method, value)
                return
        raise ValueError(f"選項 {option_key} 不存在於事件 {self.id}")

    def get_option_keys(self):
        return [opt["key"] for opt in self.options]

def load_events_from_folder(folder_path="events"):
    events = []
    for filename in Path(folder_path).glob("*.yaml"):
        with open(filename, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        for e in raw:
            events.append(Event(e))
    return events

from core.condition_parser import evaluate_condition