import os
import yaml

# 定義正確的 target 映射
target_fix_map = {
    "position": "race_info_module.position",
    "fuel": "fuel_module.fuel",
    "grip_coefficient": "tire_module.grip_coefficient",
    "acceleration": "speed_module.acceleration"
}

# 指定事件檔案所在資料夾
events_folder = "data/events"

# 遍歷所有 YAML 檔案
for filename in os.listdir(events_folder):
    if filename.endswith(".yaml"):
        filepath = os.path.join(events_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            events = yaml.safe_load(f)

        # 修正 target 欄位
        for event in events:
            for option in event.get("options", []):
                for consequence in option.get("consequences", []):
                    raw_target = consequence.get("target", "")
                    if raw_target in target_fix_map:
                        consequence["target"] = target_fix_map[raw_target]

        # 將修正後的內容寫回檔案
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(events, f, allow_unicode=True, sort_keys=False)
