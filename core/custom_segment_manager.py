# core/custom_segment_manager.py
import yaml
import os

CUSTOM_SEG_PATH = "data/segments/custom_segments.yaml"

def load_custom_segments():
    if not os.path.exists(CUSTOM_SEG_PATH):
        return {}
    with open(CUSTOM_SEG_PATH, "r", encoding="utf-8") as f:
        segs = yaml.safe_load(f)
    return {seg["id"]: seg for seg in segs}

def save_custom_segment(segment_data):
    segments = []
    if os.path.exists(CUSTOM_SEG_PATH):
        with open(CUSTOM_SEG_PATH, "r", encoding="utf-8") as f:
            segments = yaml.safe_load(f) or []
    # 移除同 ID 再加
    segments = [s for s in segments if s["id"] != segment_data["id"]]
    segments.append(segment_data)
    with open(CUSTOM_SEG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(segments, f, allow_unicode=True, sort_keys=False)

def list_custom_ids():
    return list(load_custom_segments().keys())

def generate_new_custom_id(base_id):
    existing = list_custom_ids()
    i = 1
    while f"{base_id}_custom{i}" in existing:
        i += 1
    return f"{base_id}_custom{i}"