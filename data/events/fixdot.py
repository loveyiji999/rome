import os
import yaml

def check_event_targets(event_dir):
    for filename in os.listdir(event_dir):
        if filename.endswith(".yaml"):
            filepath = os.path.join(event_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    events = yaml.safe_load(file)
                    for event in events:
                        for option in event.get('options', []):
                            for consequence in option.get('consequences', []):
                                target = consequence.get('target', '')
                                if '.' not in target:
                                    print(f"格式錯誤的 target: '{target}' 在檔案: {filename}")
                except yaml.YAMLError as exc:
                    print(f"讀取 YAML 檔案時出錯: {filename}，錯誤訊息: {exc}")

# 使用範例
event_directory = 'data/events'  # 請根據實際路徑修改
check_event_targets(event_directory)
