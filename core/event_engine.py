import yaml
import random
from pathlib import Path
from core.condition_parser import evaluate_condition

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
        self.mutex = data.get("mutex")

    def is_triggered(self, segment, car_state, random_obj, context):
        if self.cooldown_remaining > 0:
            return False

        if segment.track_type.value not in self.trigger.get("segment_type", []):
            return False

        for cond in self.trigger.get("conditions", []):
            if not evaluate_condition(cond, car_state, context):
                return False

        prob = self.trigger.get("probability", 0.0)
        # 動態機率加成（可選）
        for dp in self.trigger.get("dynamic_probability", []):
            if evaluate_condition(dp, car_state, context):
                prob += dp.get("bonus", 0.0)
        # 限制最大不超過 1.0
        prob = min(prob, 1.0)
        return random_obj.random() < prob

    def apply_option(self, option_key, car_state):
        """
        Apply the chosen option's consequences to car_state,
        and return a randomly selected feedback message (or None).
        """
        for opt in self.options:
            if opt["key"] == option_key:
                # 1. apply consequences
                for effect in opt.get("consequences", []):
                    target = effect["target"]
                    delta = effect["delta"]
                    for method, value in delta.items():
                        car_state.apply_change(target, method, value)

                # 2. pick feedback
                feedback_list = opt.get("feedback", [])
                if feedback_list:
                    feedback_msg = random.choice(feedback_list)
                    # If you later want templating, you can uncomment and adapt:
                    # feedback_msg = feedback_msg.format(
                    #     speed=car_state.get('speed_module.speed'),
                    #     tire_wear=car_state.get('tire_module.tire_wear'),
                    #     gap=car_state.get('race_info_module.gap_to_leader')
                    # )
                    return feedback_msg
                return None

        raise ValueError(f"選項 {option_key} 不存在於事件 {self.id}")  # :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}

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
