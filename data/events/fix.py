import os
import yaml

# 資料夾路徑
EVENT_DIR = "data/events"

def add_empty_feedback_to_events():
    for fname in os.listdir(EVENT_DIR):
        if not fname.endswith(".yaml"):
            continue
        file_path = os.path.join(EVENT_DIR, fname)
        with open(file_path, "r", encoding="utf-8") as f:
            events = yaml.safe_load(f) or []

        modified = False
        # 確保 events 是列表
        if isinstance(events, list):
            for event in events:
                options = event.get("options", [])
                for opt in options:
                    if "feedback" not in opt:
                        opt["feedback"] = []
                        modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(events, f, allow_unicode=True, sort_keys=False)
            print(f"已為 {fname} 中的選項加入空的 feedback 欄位")

if __name__ == "__main__":
    add_empty_feedback_to_events()
