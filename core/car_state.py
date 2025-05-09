import yaml
import os

class CarState:
    def __init__(self, schema_path="car_state_schema.yaml", limits_path="car_state_limits.yaml"):
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.state = yaml.safe_load(f)
        with open(limits_path, 'r', encoding='utf-8') as f:
            self.limits = yaml.safe_load(f)

        # 狀態標記初始化
        self.flags = set()

    def get(self, key_path):
        parts = key_path.split(".")
        value = self.state
        for part in parts:
            value = value[part]
        return value

    def apply_change(self, target, method, value):
        keys = target.split(".")
        d = self.state
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        final_key = keys[-1]

        if method == "set":
            d[final_key] = value
        elif method == "add":
            d[final_key] = d.get(final_key, 0) + value
        elif method == "multiply":
            d[final_key] = d.get(final_key, 1) * value
        elif method == "add_flag":
            self.add_flag(value)
            return
        elif method == "remove_flag":
            self.remove_flag(value)
            return
        else:
            raise ValueError(f"未知變動方式：{method}")

        self._clamp_value(keys, d, final_key)

    def _clamp_value(self, key_parts, target_dict, key):
        if len(key_parts) < 2:
            return
        module = key_parts[0]
        attr = key_parts[1]
        limit_def = self.limits.get(module, {}).get(attr)
        if limit_def:
            v = target_dict[key]
            min_v = limit_def.get("min", v)
            max_v = limit_def.get("max", v)
            target_dict[key] = max(min(v, max_v), min_v)

    def add_flag(self, flag):
        self.flags.add(flag)

    def remove_flag(self, flag):
        self.flags.discard(flag)

    def has_flag(self, flag):
        return flag in self.flags

    def summary(self):
        flat = self._flatten(self.state)
        flat["status_flags"] = list(self.flags)
        return flat

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