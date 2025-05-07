# event_engine.py

import yaml
import os
from car_state import CarState
from condition_parser import evaluate_condition

class Event:
    def __init__(self, data):
        self.id = data["id"]
        self.category = data["category"]
        self.name = data["name"]
        self.description = data["description"]
        self.trigger = data["trigger"]
        self.options = data["options"]

    def is_triggered(self, segment, car_state, random_obj, context):
    # 1. 檢查賽道類型
        if segment.track_type.value not in self.trigger.get("segment_type", []):
            return False

    # 2. 檢查所有條件
        for cond in self.trigger.get("conditions", []):
            if not evaluate_condition(cond, car_state, context):
                return False

    # 3. 機率命中
        prob = self.trigger.get("probability", 0.0)
        return random_obj.random() < prob
    
    """選擇某一選項，將 consequences 套用到車輛狀態"""
    def apply_option(self, option_key, car_state: CarState):
        for opt in self.options:
            if opt["key"] == option_key:
                for effect in opt["consequences"]:
                    target = effect["target"]  # e.g. "engine_module.engine_temp"
                    delta = effect["delta"]
                    for method, value in delta.items():
                        car_state.apply_change(target, method, value)
                return
        raise ValueError(f"選項 {option_key} 不存在於事件 {self.id}")


    def get_option_keys(self):
        return [opt["key"] for opt in self.options]


def load_events_from_folder(folder_path="events"):
    """讀取所有 YAML 事件檔案，回傳 Event 物件列表"""
    events = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".yaml"):
            path = os.path.join(folder_path, filename)
            with open(path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
                for e in raw:
                    events.append(Event(e))
    return events
