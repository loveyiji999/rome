import os
import yaml
from glob import glob

# 設定事件資料夾路徑
EVENT_DIR = "data/events"

def unify_event_format():
    """統一所有事件 YAML 檔案的 trigger 機率與條件格式"""
    for file_path in glob(os.path.join(EVENT_DIR, "*.yaml")):
        with open(file_path, "r", encoding="utf-8") as f:
            events = yaml.safe_load(f) or []

        modified = False

        # 處理每個事件
        for event in events:
            # 確保 trigger 欄位存在
            trigger = event.get("trigger")
            if trigger is None:
                trigger = {}
                event["trigger"] = trigger
                modified = True

            # 1. 若事件頂層有 probability，搬到 trigger.probability
            top_prob = event.pop("probability", None)
            if top_prob is not None:
                if "probability" not in trigger:
                    trigger["probability"] = top_prob
                modified = True

            # 2. 確保 trigger.probability 欄位存在（若原本就沒有，可設 0.0）
            if "probability" not in trigger:
                trigger["probability"] = 0.0
                modified = True

            # 3. 統一 trigger.conditions 為列表格式
            cond = trigger.get("conditions")
            if cond is None:
                trigger["conditions"] = []
                modified = True
            elif not isinstance(cond, list):
                trigger["conditions"] = [cond]
                modified = True

        # 若有修改，寫回檔案
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(events, f, allow_unicode=True, sort_keys=False)
            print(f"已更新事件格式：{os.path.basename(file_path)}")

if __name__ == "__main__":
    unify_event_format()

