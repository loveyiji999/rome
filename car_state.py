import yaml
import os

class CarState:
    def __init__(self, schema_path="car_state_schema.yaml", limits_path="car_state_limits.yaml"):
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.state = yaml.safe_load(f)

        with open(limits_path, 'r', encoding='utf-8') as f:
            self.limits = yaml.safe_load(f)

    def get(self, key_path):
        parts = key_path.split(".")
        value = self.state
        for part in parts:
            value = value[part]
        return value

    def apply_change(self, key_path, method, value):
        parts = key_path.split(".")
        target = self.state
        for part in parts[:-1]:
            target = target[part]
        final_key = parts[-1]
        current = target[final_key]

        # 變更屬性
        if method == "add":
            target[final_key] += value
        elif method == "multiply":
            target[final_key] *= value
        elif method == "set":
            target[final_key] = value
        else:
            raise ValueError(f"未知變動方式：{method}")

        # 自動 clamp
        self._clamp_value(parts, target, final_key)

    def _clamp_value(self, key_parts, target_dict, key):
        module = key_parts[0]
        attr = key_parts[1]
        limit_def = self.limits.get(module, {}).get(attr)
        if limit_def:
            v = target_dict[key]
            min_v = limit_def.get("min", v)
            max_v = limit_def.get("max", v)
            target_dict[key] = max(min(v, max_v), min_v)

    def summary(self):
        return self._flatten(self.state)

    def _flatten(self, d, parent_key="", sep="."):
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten(v, new_key, sep=sep))
            else:
                items[new_key] = round(v, 2) if isinstance(v, float) else v
        return items

    def __repr__(self):
        return f"<CarState {self.summary()}>"