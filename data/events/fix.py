import os
import yaml

# 所有事件的資料夾
EVENT_DIR = "data/events"

# 預設 cooldown 數值
DEFAULT_COOLDOWN = 2

def add_cooldown_to_events():
    for fname in os.listdir(EVENT_DIR):
        if fname.endswith(".yaml"):
            full_path = os.path.join(EVENT_DIR, fname)
            with open(full_path, "r", encoding="utf-8") as f:
                events = yaml.safe_load(f)

            modified = False
            for event in events:
                if "cooldown" not in event:
                    event["cooldown"] = DEFAULT_COOLDOWN
                    modified = True

            if modified:
                with open(full_path, "w", encoding="utf-8") as f:
                    yaml.dump(events, f, allow_unicode=True, sort_keys=False)
                print(f"已加入 cooldown 至：{fname}")

if __name__ == "__main__":
    add_cooldown_to_events()